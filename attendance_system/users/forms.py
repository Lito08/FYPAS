from django import forms
from django.contrib.auth.forms import PasswordResetForm
from .models import User

class UserCreationForm(forms.ModelForm):
    personal_email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'personal_email', 'role']

    def clean_personal_email(self):
        """Check if the personal email already exists (excluding the current user when editing)."""
        personal_email = self.cleaned_data.get("personal_email")
        user_id = self.instance.id  # Get the ID of the user being edited
        
        # ✅ Exclude the current user when checking for duplicate emails
        if User.objects.exclude(id=user_id).filter(personal_email=personal_email).exists():
            raise forms.ValidationError("This personal email is already in use. Please use a different email.")
        
        return personal_email

    def save(self, commit=True):
        if self.instance.pk:  # If editing an existing user
            user = super().save(commit=False)
            if commit:
                user.save()
            return user
        else:  # If creating a new user
            user, temp_password = User.objects.create_user(
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                personal_email=self.cleaned_data['personal_email'],
                role=self.cleaned_data['role']
            )
            return user, temp_password

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form that ensures emails are sent to personal_email."""

    def get_users(self, email):
        """Override to filter by personal_email instead of email."""
        active_users = User.objects.filter(personal_email=email, is_active=True)
        
        # ✅ Ensure the correct email is used when sending the reset email
        for user in active_users:
            user.email = user.personal_email  # Force Django to use personal_email
            user.save()
        
        return active_users