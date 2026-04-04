from datetime import date
from rest_framework import serializers
from records.models import Record

class RecSerializer(serializers.ModelSerializer):
    """
    Full serializer for Record CRUD.
    - user is read-only and set automatically from request.user
    - Validates amount > 0 and date not in the future
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Record
        fields = [
            'id', 'user', 'amt', 'type', 'cat',
            'date', 'desc', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_amt(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be a positive number.')
        return value

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError('Date cannot be in the future.')
        return value

    def validate_type(self, value):
        valid = dict(Record.TxType.choices)
        if value not in valid:
            raise serializers.ValidationError(
                f'Invalid type. Choose from: {", ".join(valid.keys())}'
            )
        return value
