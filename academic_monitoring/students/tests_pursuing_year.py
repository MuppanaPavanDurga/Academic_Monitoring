from django.test import TestCase
from django.contrib.auth.models import User
from students.models import StudentProfile, Semester

class PursuingYearTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="teststudent", password="password")
        self.student = StudentProfile.objects.create(
            user=self.user,
            roll_no="TEST001",
            department="CSE",
            section="A",
            email="test@example.com"
        )

    def test_not_started(self):
        """No semester -> Not Started"""
        self.assertEqual(self.student.pursuing_year, "Not Started")

    def test_1st_year(self):
        Semester.objects.create(student=self.student, semester_no=1, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "1st Year")
        
        Semester.objects.create(student=self.student, semester_no=2, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "1st Year")

    def test_2nd_year(self):
        Semester.objects.create(student=self.student, semester_no=3, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "2nd Year")
        
        Semester.objects.create(student=self.student, semester_no=4, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "2nd Year")

    def test_3rd_year(self):
        Semester.objects.create(student=self.student, semester_no=5, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "3rd Year")

    def test_4th_year(self):
        Semester.objects.create(student=self.student, semester_no=8, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "4th Year")

    def test_completed(self):
        Semester.objects.create(student=self.student, semester_no=9, cgpa=0, actual_credits=0, acquired_credits=0, result="PASS")
        self.assertEqual(self.student.pursuing_year, "Completed")
