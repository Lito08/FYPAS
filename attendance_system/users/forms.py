from django import forms
from .models import User
import random
import string

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role']  # Exclude matric_id and email, as they will be generated

    def save(self, commit=True):
        user = super().save(commit=False)

        # Auto-generate Matric ID based on role
        prefix = {'Admin': 'A', 'Lecturer': 'L', 'Student': 'S'}.get(user.role, 'U')
        random_id = ''.join(random.choices(string.digits, k=7))
        user.matric_id = f"{prefix}{random_id}"

        # Auto-generate email based on Matric ID
        user.email = f"{user.matric_id}@university.com"

        # Generate and set a random temporary password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        user.set_password(temp_password)

        if commit:
            user.save()
        
        return user, temp_password  # Return user and password for potential email sending
