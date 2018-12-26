from rest_framework import serializers
from .models import Area


class AreasSerializer(serializers.ModelSerializer):
    """行政区序列化器"""
    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
    """子行政区序列化器"""
    subs = AreasSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')
