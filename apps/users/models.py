from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, phone, fullname=None):
        user = self.model(phone=phone, fullname=fullname)
        user.set_unusable_password()
        user.save()
        return user


class User(AbstractBaseUser):
    phone = models.CharField(max_length=15, unique=True)
    fullname = models.CharField(max_length=50)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone
