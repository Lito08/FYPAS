from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    matric_id = models.CharField(max_length=10, unique=True)
    ROLE_CHOICES = (("student", "Student"), ("lecturer", "Lecturer"), ("admin", "Admin"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    # Fix conflicts by adding custom related_name attributes
    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions", blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
