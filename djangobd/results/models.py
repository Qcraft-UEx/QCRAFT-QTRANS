from django.db import models
from circuitIdentity.models import CircuitIdentity

class Results(models.Model):
    id_circuito = models.ForeignKey(CircuitIdentity, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=100, null=True) 
    tipo_circuito = models.CharField(max_length=50)  
    timestamp = models.DateTimeField(auto_now_add=True)
    tarea_id = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'results' 

