"""
usuarios/models.py
Modelo de usuario personalizado compatible con Django Admin,
JWT y MySQL existente.
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


class UsuarioManager(BaseUserManager):

    def create_user(self, email, nombre, password=None):
        if not email:
            raise ValueError("El email es requerido")

        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password):
        user = self.create_user(email, nombre, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    idusuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fechanacimiento = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', blank=True, related_name='usuarios_usuario_set')
    user_permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='usuarios_usuario_set')
    objects = UsuarioManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]
    class Meta:
        db_table = "usuario"
    def __str__(self):
        return self.email or ""
    @property
    def id(self):
        return self.idusuario
