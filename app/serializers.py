from rest_framework import serializers
from app.models import DataBase
from datetime import datetime
DICT_MAP = {
    "заказ №": {'name': 'order_number',
                'validators': int},
    "№": {'name': 'column_number',
          'validators': int},
    "стоимость,$": {'name': 'order_cost',
                    'validators': float},
    "срок поставки": {'name': 'delivery_time',
                      'validators': str},
}


class ExtraFieldSerializerNameRow(serializers.Serializer):
    def to_internal_value(self, data):
        data = DICT_MAP.get(data).get('name')
        return {self.field_name: data}


class ExtraFieldSerializerValue(serializers.Serializer):
    def to_internal_value(self, data):
        return {self.field_name: data}


class SheetPostSerializer(serializers.ModelSerializer):
    delivery_time = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    column_index = serializers.IntegerField()
    value = ExtraFieldSerializerValue(source='*')
    name_row = ExtraFieldSerializerNameRow(source='*')

    class Meta:
        model = DataBase
        fields = ('delivery_time', 'name_row', 'column_index', 'value')

    def validate(self, validated_data):
        name_row = validated_data.pop('name_row')
        value = validated_data.pop('value')
        validated_data.update({name_row: value})
        delivery_time_str = validated_data.pop('delivery_time')
        validated_data.update({'delivery_time': datetime.strptime(delivery_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')})
        return validated_data
