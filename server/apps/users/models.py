from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import bcrypt

from .enums import Role


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Role.ADMIN.value)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.IntegerField(choices=Role.choices(), default=Role.USER.value)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.email})"

    def set_password(self, raw_password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(
            raw_password.encode('utf-8'),
            self.password.encode('utf-8')
        )

    def get_role(self):
        return Role(self.role)

    @property
    def is_staff(self):
        return self.role == Role.ADMIN.value

    @property
    def is_superuser(self):
        return self.role == Role.ADMIN.value

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
