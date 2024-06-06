from api.models import Person
from rest_framework import serializers


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            'name',
            'iin',
            'phone'
        ]
    def create(self, validated_data):
        if  Person.objects.filter(iin=validated_data['iin']).exists():
            raise serializers.ValidationError('Человек с таким ИИН уже существует.')
        return Person.objects.create(**validated_data)


