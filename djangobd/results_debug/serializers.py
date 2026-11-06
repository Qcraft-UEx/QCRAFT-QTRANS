from rest_framework import serializers
from .models import ResultsDebug

class ResultsDebugSerializer(serializers.ModelSerializer):
    
    result = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ResultsDebug
        fields = '__all__'
