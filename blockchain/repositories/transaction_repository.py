from blockchain.models import Transaction
from django.core.exceptions import ObjectDoesNotExist


class TransactionRepository:
    @staticmethod
    def create(transaction_hash, from_address, to_address, block):
        transaction = Transaction(transaction_hash=transaction_hash, from_address=from_address, to_address=to_address, block=block)
        transaction.save()
        return transaction

    @staticmethod
    def get_all():
        return Transaction.objects.all()

    @staticmethod
    def get_by_id(transaction_hash):
        try:
            return Transaction.objects.get(pk=transaction_hash)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update(transaction_hash, **kwargs):
        try:
            transaction = Transaction.objects.get(pk=transaction_hash)
            for key, value in kwargs.items():
                setattr(transaction, key, value)
            transaction.save()
            return transaction
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(transaction_hash):
        try:
            transaction = Transaction.objects.get(pk=transaction_hash)
            transaction.delete()
            return True
        except ObjectDoesNotExist:
            return False