from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .managers import UserManager
import uuid


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True,  blank=True, null=True)
    first_name = models.CharField(max_length=150,  blank=True, null=True)
    last_name = models.CharField(max_length=150,  blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    enc_password = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],  blank=True, null=True)
    location = models.CharField(max_length=255,  blank=True, null=True)  # Use for city or region
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = UserManager() 
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set', blank=True)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'



class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    interested_in = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Both', 'Both')])
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=50)
    max_distance = models.IntegerField(default=100)  # Maximum distance in km

    def __str__(self):
        return f"{self.user.username}'s Preferences"
    

class UserPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='user_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Photo"


class Interest(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.FileField(upload_to='interest-icon/')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "interests"
        verbose_name = "Interest"
        verbose_name_plural = "Interests"


class UserInterest(models.Model):  # Renamed to singular for consistency
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interests")  # Updated related_name to be more descriptive
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, blank=True, null=True)  # Added on_delete behavior for interest FK

    def __str__(self):
        return f"{self.user.first_name} - {self.interest.name}"

    class Meta:
        db_table = "user_interests"
        verbose_name = "User Interest"
        verbose_name_plural = "User Interests"