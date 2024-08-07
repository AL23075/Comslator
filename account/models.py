from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    STATUS = [
        ('online', 'on_line'),
        ('offline', 'off_line'),
    ]

    username   = models.CharField(max_length=200, null=True)
    email      = models.EmailField(unique=True, null=True)
    password   = models.CharField(max_length=100)
    birth_date = models.DateTimeField(auto_now_add=True)
    image      = models.ImageField(upload_to='media/user_icon', height_field=None, width_field=None, max_length=None)
    status     = models.CharField(choices=STATUS, max_length=50)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']
    
    object = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def is_staff(self):
        return self.is_superuser
    
