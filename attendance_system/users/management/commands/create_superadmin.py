from django.core.management.base import BaseCommand
from users.models import User
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Create the Superadmin user with matric_id, role, and email'

    def add_arguments(self, parser):
        # Adding arguments for matric_id and password
        parser.add_argument('matric_id', type=str, help='Matric ID of the Superadmin')
        parser.add_argument('password', type=str, help='Password for the Superadmin')

    def handle(self, *args, **kwargs):
        matric_id = kwargs['matric_id']
        password = kwargs['password']

        # Ensure matric_id is unique
        if User.objects.filter(matric_id=matric_id).exists():
            self.stdout.write(self.style.ERROR(f"User with matric ID {matric_id} already exists"))
            return

        try:
            # Create superadmin with predefined role 'Superadmin'
            user = User.objects.create_superuser(matric_id=matric_id, password=password, role='Superadmin')
            self.stdout.write(self.style.SUCCESS(f"Superadmin with matric_id {matric_id} created successfully"))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f"Error creating Superadmin: {e}"))
