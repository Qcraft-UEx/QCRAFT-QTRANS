# circuitIdentity/models.py

from django.db import models
from link.models import Link
from django.db.models.signals import post_delete
from django.dispatch import receiver

class CircuitIdentity(models.Model):
    email = models.EmailField()
    nombre = models.CharField(max_length=100, null=True)
    url_desplegada = models.URLField(blank=True, null=True)
    link_id = models.ManyToManyField(Link, related_name='circuit_identities')  # Nueva relación ManyToMany

    class Meta:
        db_table = 'circuitIdentity'

    def __str__(self):
        return f"{self.nombre or self.email}"

# Puedes eliminar esta señal si ya no necesitas la lógica de borrado individual por ID

