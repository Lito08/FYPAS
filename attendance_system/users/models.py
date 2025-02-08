from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, personal_email, role, **extra_fields):
        """Create and return a user with a generated Matric ID and email."""
        if not personal_email:
            raise ValueError('A personal email is required.')

        # Generate Matric ID
        prefix = {'Admin': 'A', 'Lecturer': 'L', 'Student': 'S'}.get(role, 'U')
        random_id = ''.join(random.choices(string.digits, k=7))  # FIXED: Generating ID correctly
        matric_id = f"{prefix}{random_id}"

        # Generate university email
        university_email = f"{matric_id}@university.com"

        user = self.model(
            matric_id=matric_id,
            email=university_email,
            personal_email=personal_email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            first_login=True,  # User must change password on first login
            **extra_fields
        )
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # FIXED: Generate password
        user.set_password(temp_password)
        user.save(using=self._db)
        return user, temp_password

    def create_superuser(self, matric_id, email=None, password=None, **extra_fields):
        """Create and return a superuser with a matric_id, email, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(matric_id=matric_id, email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    matric_id = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True, default="default@university.com")
    personal_email = models.EmailField(unique=True, blank=True, null=True, default="default@example.com")
    first_name = models.CharField(max_length=50, default="First")
    last_name = models.CharField(max_length=50, default="Last")
    role = models.CharField(max_length=20, choices=[
        ('Superadmin', 'Superadmin'),
        ('Admin', 'Admin'),
        ('Lecturer', 'Lecturer'),
        ('Student', 'Student')
    ])
    first_login = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'matric_id'
    REQUIRED_FIELDS = ['email', 'personal_email', 'first_name', 'last_name', 'role']

    objects = UserManager()

    def __str__(self):
        return self.matric_id
