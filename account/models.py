from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class user_account(AbstractUser):
    username = models.CharField(max_length=254, unique=True, db_index=True, primary_key=True)
    def __str__(self):
        return self.username

