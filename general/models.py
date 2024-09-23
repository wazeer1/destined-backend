from django.db import models
from django.utils import timezone
import random
from datetime import timedelta
import uuid

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField( db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)  # 6 digit OTP
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def generate_otp(self):
        """Generate a 6-digit random OTP."""
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.created_at = timezone.now()  # Reset the timestamp
        self.attempts = 0  # Reset attempts
        self.is_active = True  # Mark as active after new generation
        self.save()

    def is_expired(self):
        """Check if the OTP is expired after 3 minutes."""
        return timezone.now() > self.created_at + timedelta(minutes=3)

    def can_attempt(self):
        """Check if the user can still attempt to verify within 3 tries."""
        return self.attempts < 3

    def increment_attempts(self):
        """Increment the number of attempts made."""
        self.attempts += 1
        self.save()

    def deactivate(self):
        """Deactivate the OTP after 3 attempts or if it's expired."""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"OTP for {self.phone_number}: {self.otp_code} (Attempts: {self.attempts})"

    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        indexes = [
            models.Index(fields=['phone_number', 'otp_code']),
        ]