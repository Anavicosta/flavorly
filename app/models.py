from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone

class Receita(models.Model):
    id_receita = models.AutoField(primary_key=True) 
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)  
    categoria = models.CharField(max_length=30)  
    modo_preparo = models.TextField()

    def __str__(self):
        return self.nome

    def get_avaliacoes(self):
        return self.avaliacoes.all() 

    def media_avaliacoes(self):
        avaliacoes = self.avaliacoes.all()  
        if avaliacoes.exists():
            return sum(av.nota for av in avaliacoes) / avaliacoes.count()
        return 0

class Ingrediente(models.Model):
    receita = models.ForeignKey(Receita, related_name='ingredientes', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    quantidade = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantidade} de {self.nome}"

class Comentario(models.Model):
    receita = models.ForeignKey('Receita', on_delete=models.CASCADE)
    texto = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'

class Avaliacao(models.Model):
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nota = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ('receita', 'usuario')  
