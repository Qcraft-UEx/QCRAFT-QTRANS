from rest_framework import serializers
from .models import CircuitIdentity

class CircuitIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CircuitIdentity
        fields = '__all__'
        