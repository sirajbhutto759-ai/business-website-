from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_STAFF = 'STAFF'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin (Full Access)'),
        (ROLE_STAFF, 'Staff / Cashier'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active_staff = models.BooleanField(default=True)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = UserProfile.ROLE_ADMIN if instance.is_superuser else UserProfile.ROLE_STAFF
        UserProfile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            role = UserProfile.ROLE_ADMIN if instance.is_superuser else UserProfile.ROLE_STAFF
            UserProfile.objects.create(user=instance, role=role)
