from django.contrib import admin
from .models import *

admin.site.register(Receita)
admin.site.register(Ingrediente)
admin.site.register(Comentario)
admin.site.register(Avaliacao)