from django.db import models
from circuitIdentity.models import CircuitIdentity
from results.models import Results

class ResultsDebug(models.Model):
    id_circuito_debug = models.CharField(max_length=100, unique=True, null=False)
    url_circuito_debug = models.TextField(null=False)
    resultado_circuito_debug = models.JSONField(null=False)

    class Meta:
        db_table = 'results_debug'