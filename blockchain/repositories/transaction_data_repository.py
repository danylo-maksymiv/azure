from blockchain.models import TransactionData
from django.core.exceptions import ObjectDoesNotExist


class TransactionDataRepository:
    @staticmethod
    def create(transaction, status, value, eth_price, gas_limit, base_fee, max_fee, priority_fee, input_data, timestamp, gas_used):
        transaction_data = TransactionData(
            transaction=transaction, status=status, value=value, eth_price=eth_price,
            gas_limit=gas_limit, base_fee=base_fee, max_fee=max_fee,
            priority_fee=priority_fee, input_data=input_data, timestamp=timestamp, gas_used=gas_used
        )
        transaction_data.save()
        return transaction_data

    @staticmethod
    def get_all():
        return TransactionData.objects.all()

    @staticmethod
    def get_by_id(transaction):
        try:
            return TransactionData.objects.get(pk=transaction)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update(transaction, **kwargs):
        try:
            transaction_data = TransactionData.objects.get(pk=transaction)
            for key, value in kwargs.items():
                setattr(transaction_data, key, value)
            transaction_data.save()
            return transaction_data
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(transaction):
        try:
            transaction_data = TransactionData.objects.get(pk=transaction)
            transaction_data.delete()
            return True
        except ObjectDoesNotExist:
            return False
