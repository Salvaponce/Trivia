from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.contrib.auth.models import User


class Pregunta(models.Model):
    pregunta = models.CharField(max_length=150)
    resp_correcta = models.CharField(max_length=100)


class Respuestas(models.Model):
    texto = models.CharField(max_length = 50)
    pregunta = ForeignKey(Pregunta, on_delete=models.CASCADE)


class Score(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    point = models.IntegerField(default=0) 
