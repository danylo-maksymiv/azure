from rest_framework import serializers
from .models import *

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionData
        fields = '__all__'

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'

class ContractDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractData
        fields = '__all__'

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'

class MempoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mempool
        fields = '__all__'

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'

