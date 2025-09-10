from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model
    Inherits from AbstractUser to get all of Django's default user fields and methods.
    We add a `nickname` field for display purposes.
    """
    nickname = models.CharField(
        max_length=100, 
        unique=True, 
        blank=False, 
        null=False,
        help_text="Required. 100 characters or fewer. Letters, digits and @/./+/-/_ only.",
        error_messages={
            'unique': "A user with that nickname already exists.",
        },
    )
    profile_image = models.ImageField(
        upload_to='profile_pics', 
        blank=True, 
        null=True,
        help_text="User profile picture"
    )

    def __str__(self):
        return self.username
