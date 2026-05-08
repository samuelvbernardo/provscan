from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import ClassGroup, Student

User = get_user_model()


def make_user(email="prof@example.com", password="Test@1234"):
    return User.objects.create_user(email=email, password=password)


def make_class_group(name="Turma A", school_year="2024"):
    return ClassGroup.objects.create(name=name, school_year=school_year)


class ClassGroupModelTests(TestCase):
    def test_create_class_group(self):
        cg = make_class_group()
        self.assertEqual(str(cg), "Turma A")
        self.assertFalse(cg.is_deleted)

    def test_soft_delete(self):
        cg = make_class_group()
        cg.delete()
        self.assertTrue(cg.is_deleted)
        self.assertIsNotNone(cg.deleted_at)
        self.assertTrue(ClassGroup.objects.filter(id=cg.id).exists())
        self.assertFalse(ClassGroup.active.filter(id=cg.id).exists())

    def test_restore(self):
        cg = make_class_group()
        cg.delete()
        cg.restore()
        self.assertFalse(cg.is_deleted)
        self.assertIsNone(cg.deleted_at)
        self.assertTrue(ClassGroup.active.filter(id=cg.id).exists())

    def test_active_manager_excludes_deleted(self):
        cg1 = make_class_group(name="Ativa")
        cg2 = make_class_group(name="Deletada")
        cg2.delete()
        active = list(ClassGroup.active.values_list("name", flat=True))
        self.assertIn("Ativa", active)
        self.assertNotIn("Deletada", active)


class StudentModelTests(TestCase):
    def setUp(self):
        self.cg = make_class_group()

    def test_create_student(self):
        s = Student.objects.create(
            class_group=self.cg, name="Aluno 1", number=1
        )
        self.assertEqual(str(s), "01 - Aluno 1")

    def test_soft_delete_student(self):
        s = Student.objects.create(
            class_group=self.cg, name="Aluno 2", number=2
        )
        s.delete()
        self.assertTrue(s.is_deleted)
        self.assertFalse(Student.active.filter(id=s.id).exists())

    def test_allows_same_number_after_soft_delete(self):
        s1 = Student.objects.create(
            class_group=self.cg, name="Aluno 3", number=3
        )
        s1.delete()
        s2 = Student.objects.create(
            class_group=self.cg, name="Aluno 3 Novo", number=3
        )
        self.assertIsNotNone(s2.id)

    def test_students_count_excludes_deleted(self):
        Student.objects.create(class_group=self.cg, name="A1", number=1)
        s2 = Student.objects.create(class_group=self.cg, name="A2", number=2)
        s2.delete()
        count = self.cg.students.filter(is_deleted=False).count()
        self.assertEqual(count, 1)


class ClassGroupAPITests(APITestCase):
    URL = "/api/v1/class-groups/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def test_list_class_groups(self):
        make_class_group(name="Turma B")
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data["count"], 1)

    def test_create_class_group(self):
        res = self.client.post(
            self.URL,
            {"name": "Nova Turma", "school_year": "2024", "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Nova Turma")
        self.assertIn("students_count", res.data)

    def test_create_class_group_without_name_returns_400(self):
        res = self.client.post(
            self.URL, {"name": "", "is_active": True}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_class_group_soft_deletes(self):
        cg = make_class_group(name="Para Deletar")
        res = self.client.delete(f"{self.URL}{cg.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        cg.refresh_from_db()
        self.assertTrue(cg.is_deleted)

    def test_deleted_class_group_not_in_list(self):
        cg = make_class_group(name="Invisível")
        cg.delete()
        res = self.client.get(self.URL)
        names = [item["name"] for item in res.data["results"]]
        self.assertNotIn("Invisível", names)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_nonexistent_returns_404(self):
        res = self.client.get(f"{self.URL}99999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_students_count_in_list_reflects_active_students(self):
        cg = make_class_group(name="Turma Contagem")
        Student.objects.create(class_group=cg, name="Ativo", number=1)
        deleted = Student.objects.create(class_group=cg, name="Deletado", number=2)
        deleted.delete()
        res = self.client.get(self.URL)
        item = next(r for r in res.data["results"] if r["name"] == "Turma Contagem")
        self.assertEqual(item["students_count"], 1)

    def test_students_count_is_zero_on_create(self):
        res = self.client.post(
            self.URL,
            {"name": "Turma Zero", "school_year": "2024", "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["students_count"], 0)


class StudentAPITests(APITestCase):
    URL = "/api/v1/students/"

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.cg = make_class_group(name="Turma Alunos")

    def test_create_student(self):
        res = self.client.post(
            self.URL,
            {"name": "João Silva", "number": 5, "class_group": self.cg.id, "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "João Silva")

    def test_create_student_without_name_returns_400(self):
        res = self.client.post(
            self.URL,
            {"name": "", "number": 1, "class_group": self.cg.id, "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_student_without_class_group_returns_400(self):
        res = self.client.post(
            self.URL,
            {"name": "Sem Turma", "number": 1, "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_student_number_out_of_range_returns_400(self):
        res = self.client.post(
            self.URL,
            {"name": "Fora do Limite", "number": 100, "class_group": self.cg.id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_number_in_same_class_returns_400(self):
        Student.objects.create(class_group=self.cg, name="Aluno 1", number=10)
        res = self.client.post(
            self.URL,
            {"name": "Aluno 2", "number": 10, "class_group": self.cg.id, "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_number_allowed_in_different_classes(self):
        cg2 = make_class_group(name="Outra Turma")
        Student.objects.create(class_group=self.cg, name="Aluno A", number=1)
        res = self.client.post(
            self.URL,
            {"name": "Aluno B", "number": 1, "class_group": cg2.id, "is_active": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_student_soft_deletes(self):
        s = Student.objects.create(class_group=self.cg, name="Para Deletar", number=99)
        res = self.client.delete(f"{self.URL}{s.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        s.refresh_from_db()
        self.assertTrue(s.is_deleted)

    def test_filter_by_class_group(self):
        cg2 = make_class_group(name="Turma Filtro")
        Student.objects.create(class_group=self.cg, name="Da Turma A", number=1)
        Student.objects.create(class_group=cg2, name="Da Turma B", number=1)
        res = self.client.get(f"{self.URL}?class_group={self.cg.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data["results"]:
            self.assertEqual(item["class_group"], self.cg.id)
