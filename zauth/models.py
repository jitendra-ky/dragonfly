from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    '''
    Custom user model for the application
    email -> modified to unique and not blank
    '''
    email = models.EmailField(_("email address"), unique=True)
