from django.db import models
from django.contrib.auth.models import User

class Pratica(models.Model):
    nome_pratica = models.CharField(max_length=100)
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pratiche_fiscali")
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_pratica
