from django.db import models
from link.models import Link
from django.db.models.signals import post_delete
from django.dispatch import receiver

# class CircuitIdentity(models.Model):
#     email = models.EmailField()
#     nombre = models.CharField(max_length=100, null=True)
#     url_desplegada = models.URLField(blank=True, null=True)
#     link_id = models.ManyToManyField(Link, related_name='circuit_identities')

#     class Meta:
#         db_table = 'circuitIdentity'

#     def __str__(self):
#         return f"{self.nombre or self.email}"

# class CustomGate(models.Model):
#     email = models.EmailField()
#     gate_id = models.CharField(max_length=100)
#     name = models.CharField(max_length=100)
#     symbol = models.CharField(max_length=20)
#     definition = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     links = models.ManyToManyField(Link, related_name='custom_gates', blank=True)

#     class Meta:
#         db_table = 'customGate'
#         unique_together = ('email', 'name')

#     def __str__(self):
#         return f"{self.symbol} ({self.name}) - {self.email}"


class CircuitIdentity(models.Model):
    email = models.EmailField()
    nombre = models.CharField(max_length=100, null=True)
    url_desplegada = models.URLField(blank=True, null=True)
    link_id = models.ManyToManyField(Link, related_name='circuit_identities')

    class Meta:
        db_table = 'circuitIdentity'

    def __str__(self):
        return f"{self.nombre or self.email}"

class CustomGate(models.Model):
    email = models.EmailField()
    gate_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    definition = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    links = models.ManyToManyField(Link, related_name='custom_gates', blank=True)

    class Meta:
        db_table = 'customGate'
        unique_together = ('email', 'name')

    def __str__(self):
        return f"{self.symbol} ({self.name}) - {self.email}"