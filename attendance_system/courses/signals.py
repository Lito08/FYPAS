from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import Section, ClassSession

@receiver(post_save, sender=Section)
def create_class_sessions(sender, instance, created, **kwargs):
    """Automatically generates 14 weeks of class sessions based on the first scheduled date"""
    if created and instance.start_date and instance.class_time:
        # ✅ Delete any existing sessions for this section
        ClassSession.objects.filter(section=instance).delete()

        # ✅ Generate 14 class sessions
        for week in range(1, 15):  # Weeks 1 - 14
            session_date = instance.start_date + timedelta(weeks=week-1)
            ClassSession.objects.create(
                section=instance,
                week_number=week,
                date=session_date,
                start_time=instance.class_time
            )
