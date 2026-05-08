import io
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import ClassGroup, Student
from omr.models import Exam, ScanResult
from omr.api.v1.serializers import ExamSerializer

User = get_user_model()


def make_user(email="prof@example.com", password="Test@1234"):
    return User.objects.create_user(email=email, password=password)


def make_class_group(name="Turma OMR"):
    return ClassGroup.objects.create(name=name, school_year="2024")


def make_exam(cg, title="Prova Teste", questions=10, options=4):
    answer_key = ["A", "B", "C", "D"] * (questions // 4) + ["A"] * (questions % 4)
    return Exam.objects.create(
        title=title,
        class_group=cg,
        questions_count=questions,
        options_count=options,
        answer_key=answer_key[:questions],
        is_active=True,
    )


def make_png_image():
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile("cartao.png", buf.read(), content_type="image/png")


class ExamSerializerTests(TestCase):
    def setUp(self):
        self.cg = make_class_group()
        self.base = {
            "title": "Prova X",
            "class_group": self.cg.id,
            "questions_count": 10,
            "options_count": 4,
            "answer_key": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"],
            "is_active": True,
        }

    def test_valid_data(self):
        s = ExamSerializer(data=self.base)
        self.assertTrue(s.is_valid(), s.errors)

    def test_questions_count_below_minimum(self):
        data = {**self.base, "questions_count": 7, "answer_key": ["A"] * 7}
        s = ExamSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("questions_count", s.errors)

    def test_questions_count_above_maximum(self):
        data = {**self.base, "questions_count": 31, "answer_key": ["A"] * 31}
        s = ExamSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("questions_count", s.errors)

    def test_invalid_options_count(self):
        data = {**self.base, "options_count": 3}
        s = ExamSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("options_count", s.errors)

    def test_answer_key_wrong_length(self):
        data = {**self.base, "answer_key": ["A", "B", "C"]}
        s = ExamSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("answer_key", s.errors)

    def test_answer_key_invalid_option(self):
        data = {**self.base, "answer_key": ["A"] * 9 + ["F"]}
        s = ExamSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("answer_key", s.errors)

    def test_answer_key_e_valid_with_5_options(self):
        data = {
            **self.base,
            "options_count": 5,
            "answer_key": ["E"] * 10,
        }
        s = ExamSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_answer_key_e_invalid_with_4_options(self):
        data = {**self.base, "answer_key": ["E"] * 10}
        s = ExamSerializer(data=data)
        self.assertFalse(s.is_valid())


class ExamAPITests(APITestCase):
    URL = "/api/v1/exams/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group()

    @patch("omr.api.v1.viewsets.generate_exam_template", return_value="exam_templates/test.pdf")
    def test_create_exam(self, mock_pdf):
        res = self.client.post(
            self.URL,
            {
                "title": "Prova API",
                "class_group": self.cg.id,
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
    def test_create_exam_without_title_returns_400(self, _):
        res = self.client.post(
            self.URL,
            {
                "title": "",
                "class_group": self.cg.id,
                "questions_count": 10,
                "options_count": 4,
                "answer_key": ["A"] * 10,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_exams(self):
        make_exam(self.cg)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data["count"], 1)

    @patch("omr.api.v1.viewsets.generate_exam_template", return_value="exam_templates/test.pdf")
    def test_delete_exam_soft_deletes(self, _):
        exam = make_exam(self.cg)
        res = self.client.delete(f"{self.URL}{exam.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exam.refresh_from_db()
        self.assertTrue(exam.is_deleted)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ScanResultAPITests(APITestCase):
    URL = "/api/v1/scan-results/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group()
        self.exam = make_exam(self.cg)

    def test_list_scan_results(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_scan_results_is_read_only(self):
        res = self.client.post(self.URL, {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_nonexistent_returns_404(self):
        res = self.client.get(f"{self.URL}99999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class OMRScanAPITests(APITestCase):
    URL = "/api/v1/omr/scan/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group()
        self.exam = make_exam(self.cg)

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
        student = Student.objects.create(
            class_group=self.cg, name="Maria", number=5
        )
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
        res = self.client.post(
            self.URL,
            {"exam_id": self.exam.id},
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_scan_without_exam_id_returns_400(self):
        res = self.client.post(
            self.URL,
            {"image": make_png_image()},
            format="multipart",
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
