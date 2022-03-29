from django.contrib import admin

from trivia_app.models import Pregunta, Respuestas, Score

# Register your models here.
admin.site.register(Pregunta)
admin.site.register(Respuestas)
admin.site.register(Score)