from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, matric_id, email=None, password=None, **extra_fields):
        """
        Create and return a user with a matric_id, email, and password.
        """
        if not matric_id:
            raise ValueError('The Matric ID must be set')
        email = email or f"{matric_id}@university.com"  # Generate email based on Matric ID
        user = self.model(matric_id=matric_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matric_id, email=None, password=None, **extra_fields):
        """
        Create and return a superuser with a matric_id, email, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(matric_id, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    matric_id = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('Superadmin', 'Superadmin'), ('Admin', 'Admin'), 
                                                     ('Lecturer', 'Lecturer'), ('Student', 'Student')])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'matric_id'
    REQUIRED_FIELDS = ['email']  # email will be automatically generated

    objects = UserManager()

    def __str__(self):
        return self.matric_id

    def generate_temp_password(self):
        """Generate a temporary password and send it to the user's email."""
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.set_password(password)
        # Logic to send the password to the user's email
        return password
