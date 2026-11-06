from django.db import models
from results.models import Results

class Deployment(models.Model):
    email = models.EmailField()
    public_AWS = models.CharField(max_length=100, null=True)
    private_AWS = models.CharField(max_length=100, null=True)
    s3_AWS = models.CharField(max_length=100, null=True)
    token_IBM = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'deployment'  