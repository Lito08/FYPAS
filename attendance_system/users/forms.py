from django import forms
from .models import User

class UserCreationForm(forms.ModelForm):
    personal_email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'personal_email', 'role']

    def clean_personal_email(self):
        """Check if the personal email already exists."""
        personal_email = self.cleaned_data.get("personal_email")
        if User.objects.filter(personal_email=personal_email).exists():
            raise forms.ValidationError("This personal email is already in use. Please use a different email.")
        return personal_email

    def save(self, commit=True):
        user, temp_password = User.objects.create_user(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            personal_email=self.cleaned_data['personal_email'],
            role=self.cleaned_data['role']
        )
        return user, temp_password
