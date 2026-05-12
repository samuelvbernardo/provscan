import io
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import ClassGroup, Student
from omr.models import Exam, ScanResult
from omr.api.v1.serializers import ExamSerializer
from omr.services.report import _calculate_stats, generate_report_card

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(email="prof@example.com", password="Test@1234"):
    return User.objects.create_user(email=email, password=password)


def make_class_group(name="Turma OMR", owner=None):
    return ClassGroup.objects.create(name=name, school_year="2024", owner=owner)


def make_exam(cg, title="Prova Teste", questions=10, options=4, owner=None):
    answer_key = ["A", "B", "C", "D"] * (questions // 4) + ["A"] * (questions % 4)
    exam = Exam.objects.create(
        title=title,
        questions_count=questions,
        options_count=options,
        answer_key=answer_key[:questions],
        is_active=True,
        owner=owner,
    )
    exam.class_groups.add(cg)
    return exam


def make_png_image():
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile("cartao.png", buf.read(), content_type="image/png")


# ---------------------------------------------------------------------------
# ExamSerializer — validações de gabarito
# ---------------------------------------------------------------------------

class ExamSerializerTests(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.cg = make_class_group(owner=self.owner)
        self.base = {
            "title": "Prova X",
            "class_groups": [self.cg.id],
            "questions_count": 10,
            "options_count": 4,
            "answer_key": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"],
            "is_active": True,
        }

    def _serializer(self, data):
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = Request(factory.post("/"))
        request.user = self.owner
        return ExamSerializer(data=data, context={"request": request})

    def test_valid_data(self):
        s = self._serializer(self.base)
        self.assertTrue(s.is_valid(), s.errors)

    def test_questions_count_below_minimum(self):
        data = {**self.base, "questions_count": 7, "answer_key": ["A"] * 7}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())
        self.assertIn("questions_count", s.errors)

    def test_questions_count_above_maximum(self):
        data = {**self.base, "questions_count": 31, "answer_key": ["A"] * 31}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())
        self.assertIn("questions_count", s.errors)

    def test_invalid_options_count(self):
        data = {**self.base, "options_count": 3}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())
        self.assertIn("options_count", s.errors)

    def test_answer_key_wrong_length(self):
        data = {**self.base, "answer_key": ["A", "B", "C"]}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())
        self.assertIn("answer_key", s.errors)

    def test_answer_key_invalid_option(self):
        data = {**self.base, "answer_key": ["A"] * 9 + ["F"]}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())
        self.assertIn("answer_key", s.errors)

    def test_answer_key_e_valid_with_5_options(self):
        data = {**self.base, "options_count": 5, "answer_key": ["E"] * 10}
        s = self._serializer(data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_answer_key_e_invalid_with_4_options(self):
        data = {**self.base, "answer_key": ["E"] * 10}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())

    def test_class_group_from_other_user_rejected(self):
        other_user = make_user(email="other@test.com")
        foreign_cg = make_class_group(name="Turma Alheia", owner=other_user)
        data = {**self.base, "class_groups": [foreign_cg.id]}
        s = self._serializer(data)
        self.assertFalse(s.is_valid())
        self.assertIn("class_groups", s.errors)


# ---------------------------------------------------------------------------
# API — Exam (com isolamento por owner)
# ---------------------------------------------------------------------------

class ExamAPITests(APITestCase):
    URL = "/api/v1/exams/"

    def setUp(self):
        self.user = make_user()
        self.other_user = make_user(email="other@example.com")
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group(owner=self.user)

    @patch("omr.api.v1.viewsets.generate_exam_template", return_value="exam_templates/test.pdf")
    def test_create_exam(self, mock_pdf):
        res = self.client.post(
            self.URL,
            {
                "title": "Prova API",
                "class_groups": [self.cg.id],
                "questions_count": 10,
                "options_count": 4,
                "answer_key": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"],
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Prova API")
        mock_pdf.assert_called_once()

    @patch("omr.api.v1.viewsets.generate_exam_template", return_value="exam_templates/test.pdf")
    def test_create_exam_sets_owner(self, _):
        res = self.client.post(
            self.URL,
            {
                "title": "Prova Owner",
                "class_groups": [self.cg.id],
                "questions_count": 10,
                "options_count": 4,
                "answer_key": ["A"] * 10,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exam = Exam.objects.get(id=res.data["id"])
        self.assertEqual(exam.owner, self.user)

    @patch("omr.api.v1.viewsets.generate_exam_template", return_value="exam_templates/test.pdf")
    def test_create_exam_without_title_returns_400(self, _):
        res = self.client.post(
            self.URL,
            {
                "title": "",
                "class_groups": [self.cg.id],
                "questions_count": 10,
                "options_count": 4,
                "answer_key": ["A"] * 10,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_exams(self):
        make_exam(self.cg, owner=self.user)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data["count"], 1)

    @patch("omr.api.v1.viewsets.generate_exam_template", return_value="exam_templates/test.pdf")
    def test_delete_exam_soft_deletes(self, _):
        exam = make_exam(self.cg, owner=self.user)
        res = self.client.delete(f"{self.URL}{exam.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exam.refresh_from_db()
        self.assertTrue(exam.is_deleted)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_see_other_users_exams(self):
        """Prova de outro usuário não aparece na listagem."""
        other_cg = make_class_group(name="Turma do Outro", owner=self.other_user)
        make_exam(other_cg, title="Prova Alheia", owner=self.other_user)
        make_exam(self.cg, title="Minha Prova", owner=self.user)
        res = self.client.get(self.URL)
        titles = [item["title"] for item in res.data["results"]]
        self.assertIn("Minha Prova", titles)
        self.assertNotIn("Prova Alheia", titles)

    def test_user_cannot_delete_other_users_exam(self):
        """DELETE em prova de outro usuário retorna 404."""
        other_cg = make_class_group(name="Outra Turma", owner=self.other_user)
        other_exam = make_exam(other_cg, owner=self.other_user)
        res = self.client.delete(f"{self.URL}{other_exam.id}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# API — ScanResult
# ---------------------------------------------------------------------------

class ScanResultAPITests(APITestCase):
    URL = "/api/v1/scan-results/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group(owner=self.user)
        self.exam = make_exam(self.cg, owner=self.user)

    def test_list_scan_results(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_scan_results_is_read_only(self):
        res = self.client.post(self.URL, {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_nonexistent_returns_404(self):
        res = self.client.get(f"{self.URL}99999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_see_other_users_scan_results(self):
        """Resultados de scans de outro usuário não aparecem na listagem."""
        other_user = make_user(email="other2@example.com")
        other_cg = make_class_group(name="Outra Turma", owner=other_user)
        other_exam = make_exam(other_cg, owner=other_user)
        ScanResult.objects.create(
            exam=other_exam,
            student_number="01",
            answers=["A"] * 10,
            score=10,
            total_questions=10,
        )
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 0)


# ---------------------------------------------------------------------------
# API — OMR Scan
# ---------------------------------------------------------------------------

class OMRScanAPITests(APITestCase):
    URL = "/api/v1/omr/scan/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group(owner=self.user)
        self.exam = make_exam(self.cg, owner=self.user)

    def _mock_result(self):
        return {
            "numero_aluno": "05",
            "respostas": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"],
            "nota": 10,
        }

    @patch("omr.api.v1.viewsets.process_image")
    def test_scan_returns_201_with_result(self, mock_pi):
        mock_pi.return_value = self._mock_result()
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["score"], 10)
        self.assertEqual(res.data["total_questions"], 10)

    @patch("omr.api.v1.viewsets.process_image")
    def test_scan_identifies_student(self, mock_pi):
        student = Student.objects.create(class_group=self.cg, name="Maria", number=5)
        mock_pi.return_value = self._mock_result()
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["student_identified"])
        self.assertEqual(res.data["student_name"], "Maria")

    @patch("omr.api.v1.viewsets.process_image")
    def test_scan_unidentified_student(self, mock_pi):
        mock_pi.return_value = {**self._mock_result(), "numero_aluno": "??"}
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertFalse(res.data["student_identified"])

    @patch("omr.api.v1.viewsets.process_image")
    def test_scan_pipeline_error_returns_422(self, mock_pi):
        mock_pi.side_effect = Exception("OpenCV falhou")
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("detail", res.data)

    def test_scan_nonexistent_exam_returns_404(self):
        res = self.client.post(
            self.URL,
            {"exam_id": 99999, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_scan_without_image_returns_400(self):
        res = self.client.post(self.URL, {"exam_id": self.exam.id}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_scan_without_exam_id_returns_400(self):
        res = self.client.post(
            self.URL, {"image": make_png_image()}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_scan_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("omr.api.v1.viewsets.process_image")
    def test_scan_creates_scan_result_in_db(self, mock_pi):
        mock_pi.return_value = self._mock_result()
        before = ScanResult.objects.count()
        self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(ScanResult.objects.count(), before + 1)

    @patch("omr.api.v1.viewsets.process_image")
    def test_scan_warnings_for_blank_answers(self, mock_pi):
        mock_pi.return_value = {
            "numero_aluno": "??",
            "respostas": [None] * 10,
            "nota": 0,
        }
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertGreater(len(res.data["warnings"]), 0)

    def test_scan_image_too_large_returns_400(self):
        large_image = SimpleUploadedFile(
            "grande.png",
            b"x" * (20 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id, "image": large_image},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", res.data)

    def test_scan_other_users_exam_returns_404(self):
        """Usuário não pode escanear prova de outro usuário."""
        other_user = make_user(email="other_scan@example.com")
        other_cg = make_class_group(name="Turma Alheia", owner=other_user)
        other_exam = make_exam(other_cg, owner=other_user)
        res = self.client.post(
            self.URL,
            {"exam_id": other_exam.id, "image": make_png_image()},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Helpers para testes de relatório
# ---------------------------------------------------------------------------

def make_scan_result(exam, student=None, answers=None, score=None, student_number="01"):
    if answers is None:
        answers = exam.answer_key[:]
    if score is None:
        score = sum(1 for a, k in zip(answers, exam.answer_key) if a == k)
    return ScanResult.objects.create(
        exam=exam,
        student=student,
        student_number=student_number,
        answers=answers,
        score=score,
        total_questions=exam.questions_count,
    )


# ---------------------------------------------------------------------------
# Unit tests — _calculate_stats
# ---------------------------------------------------------------------------

class ReportStatsTests(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.cg = make_class_group(owner=self.owner)
        self.exam = make_exam(self.cg, owner=self.owner)

    def test_single_student_is_rank_1(self):
        sr = make_scan_result(self.exam)
        stats = _calculate_stats(sr)
        self.assertEqual(stats["rank"], 1)
        self.assertEqual(stats["total_students"], 1)

    def test_rank_and_percentile_with_multiple_students(self):
        sr_top = make_scan_result(self.exam, score=10, student_number="01")
        sr_mid = make_scan_result(self.exam, score=8, student_number="02")
        sr_bot = make_scan_result(self.exam, score=6, student_number="03")

        top_stats = _calculate_stats(sr_top)
        mid_stats = _calculate_stats(sr_mid)
        bot_stats = _calculate_stats(sr_bot)

        self.assertEqual(top_stats["rank"], 1)
        self.assertEqual(mid_stats["rank"], 2)
        self.assertEqual(bot_stats["rank"], 3)

        self.assertEqual(top_stats["percentile"], round(2 / 3 * 100, 1))
        self.assertEqual(mid_stats["percentile"], round(1 / 3 * 100, 1))
        self.assertEqual(bot_stats["percentile"], 0.0)

    def test_ci_all_correct(self):
        make_scan_result(self.exam, student_number="01")
        make_scan_result(self.exam, student_number="02")
        sr = make_scan_result(self.exam, student_number="03")
        stats = _calculate_stats(sr)
        self.assertTrue(all(ci == 100.0 for ci in stats["ci_per_question"]))

    def test_ci_none_correct(self):
        wrong = ["D", "C", "B", "A"] * (self.exam.questions_count // 4)
        wrong = wrong[: self.exam.questions_count]
        make_scan_result(self.exam, answers=wrong, score=0, student_number="01")
        make_scan_result(self.exam, answers=wrong, score=0, student_number="02")
        sr = make_scan_result(self.exam, answers=wrong, score=0, student_number="03")
        stats = _calculate_stats(sr)
        self.assertTrue(all(ci == 0.0 for ci in stats["ci_per_question"]))

    def test_ci_partial_correct(self):
        key = self.exam.answer_key[:]
        wrong_q1 = [("D" if key[0] != "D" else "C")] + key[1:]
        make_scan_result(self.exam, answers=key, student_number="01")
        make_scan_result(self.exam, answers=key, student_number="02")
        make_scan_result(
            self.exam, answers=wrong_q1,
            score=self.exam.questions_count - 1, student_number="03"
        )
        sr = make_scan_result(
            self.exam, answers=wrong_q1,
            score=self.exam.questions_count - 1, student_number="04"
        )
        stats = _calculate_stats(sr)
        self.assertEqual(stats["ci_per_question"][0], 50.0)

    def test_ci_length_matches_questions(self):
        sr = make_scan_result(self.exam)
        stats = _calculate_stats(sr)
        self.assertEqual(len(stats["ci_per_question"]), self.exam.questions_count)

    def test_tied_students_same_rank(self):
        sr_a = make_scan_result(self.exam, score=10, student_number="01")
        sr_b = make_scan_result(self.exam, score=10, student_number="02")
        make_scan_result(self.exam, score=5, student_number="03")
        self.assertEqual(
            _calculate_stats(sr_a)["rank"],
            _calculate_stats(sr_b)["rank"],
        )

    def test_blank_answers_handled_in_ci(self):
        blank = [None] * self.exam.questions_count
        sr = make_scan_result(self.exam, answers=blank, score=0, student_number="01")
        stats = _calculate_stats(sr)
        self.assertEqual(len(stats["ci_per_question"]), self.exam.questions_count)


# ---------------------------------------------------------------------------
# Unit tests — generate_report_card
# ---------------------------------------------------------------------------

class GenerateReportCardTests(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.cg = make_class_group(owner=self.owner)
        self.exam = make_exam(self.cg, owner=self.owner)

    def test_returns_bytes(self):
        sr = make_scan_result(self.exam)
        result = generate_report_card(sr)
        self.assertIsInstance(result, bytes)

    def test_is_valid_pdf(self):
        sr = make_scan_result(self.exam)
        pdf = generate_report_card(sr)
        self.assertTrue(pdf.startswith(b"%PDF"), "Bytes não são um PDF válido")

    def test_pdf_with_identified_student(self):
        student = Student.objects.create(class_group=self.cg, name="Ana Laura", number=1)
        sr = make_scan_result(self.exam, student=student, student_number="01")
        pdf = generate_report_card(sr)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_pdf_with_unidentified_student(self):
        sr = make_scan_result(self.exam, student=None, student_number="??")
        pdf = generate_report_card(sr)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_pdf_with_all_blank_answers(self):
        blank = [None] * self.exam.questions_count
        sr = make_scan_result(self.exam, answers=blank, score=0)
        pdf = generate_report_card(sr)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_pdf_not_empty(self):
        sr = make_scan_result(self.exam)
        pdf = generate_report_card(sr)
        self.assertGreater(len(pdf), 1024, "PDF muito pequeno — provavelmente vazio")


# ---------------------------------------------------------------------------
# API — Report endpoint
# ---------------------------------------------------------------------------

class ReportCardAPITests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group(owner=self.user)
        self.exam = make_exam(self.cg, owner=self.user)
        self.scan_result = make_scan_result(self.exam)

    def _url(self, pk=None):
        pk = pk or self.scan_result.id
        return f"/api/v1/scan-results/{pk}/report/"

    def test_returns_200(self):
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_content_type_is_pdf(self):
        res = self.client.get(self._url())
        self.assertEqual(res["Content-Type"], "application/pdf")

    def test_response_is_valid_pdf(self):
        res = self.client.get(self._url())
        self.assertTrue(res.content.startswith(b"%PDF"))

    def test_content_disposition_is_attachment(self):
        res = self.client.get(self._url())
        self.assertIn("attachment", res["Content-Disposition"])
        self.assertIn(".pdf", res["Content-Disposition"])

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_returns_404(self):
        res = self.client.get(self._url(pk=99999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_users_scan_result_returns_404(self):
        """Usuário não pode acessar boletim de scan de outro usuário."""
        other_user = make_user(email="other_report@example.com")
        other_cg = make_class_group(name="Turma Rival", owner=other_user)
        other_exam = make_exam(other_cg, owner=other_user)
        other_sr = make_scan_result(other_exam)
        res = self.client.get(self._url(pk=other_sr.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_pdf_size_is_reasonable(self):
        res = self.client.get(self._url())
        self.assertGreater(len(res.content), 1024)
        self.assertLess(len(res.content), 5 * 1024 * 1024)
