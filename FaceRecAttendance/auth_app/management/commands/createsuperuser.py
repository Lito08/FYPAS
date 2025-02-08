from django.core.management.commands import createsuperuser
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError

class Command(createsuperuser.Command):
    help = "Create a superuser and automatically assign the role as 'admin'"

    def handle(self, *args, **options):
        # Automatically assign the role as 'admin' for superusers
        options['role'] = 'admin'  # Set role to 'admin' (superadmin)
        
        try:
            # Run the original createsuperuser command to create the superuser
            super().handle(*args, **options)
        except IntegrityError as e:
            # If the superuser already exists, handle the exception gracefully
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
