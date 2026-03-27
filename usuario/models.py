from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    documento = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username