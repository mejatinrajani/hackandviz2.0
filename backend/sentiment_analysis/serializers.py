# sentiment/serializers.py

from rest_framework import serializers

class SentimentInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000)
