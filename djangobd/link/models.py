# En link/models.py

from django.db import models

class Link(models.Model):
    url = models.URLField()
    cadena = models.CharField(max_length=20, blank=True, null=True)
    screenshot = models.ImageField(upload_to='screenshots/', null=True, blank=True)

    def __str__(self):
        return self.url

    class Meta:
        db_table = 'link'  
