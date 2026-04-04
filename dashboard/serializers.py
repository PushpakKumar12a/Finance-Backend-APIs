from rest_framework import serializers

class SummSerializer(serializers.Serializer):
    "Overall financial summary."
    inc = serializers.DecimalField(max_digits=14, decimal_places=2)
    exp = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    recs = serializers.IntegerField()

class CatBreakdownSerializer(serializers.Serializer):
    "Per-category totals."
    cat = serializers.CharField()
    type = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()

class TrendSerializer(serializers.Serializer):
    "Monthly income/expense trend data point."
    month = serializers.DateField(format='%Y-%m')
    type = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()
