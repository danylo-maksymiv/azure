from blockchain.models import Mempool
from django.core.exceptions import ObjectDoesNotExist


class MempoolRepository:
    @staticmethod
    def create(transaction):
        mempool = Mempool(transaction=transaction)
        mempool.save()
        return mempool

    @staticmethod
    def get_all():
        return Mempool.objects.all()

    @staticmethod
    def get_by_id(transaction):
        try:
            return Mempool.objects.get(pk=transaction)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(transaction):
        try:
            mempool = Mempool.objects.get(pk=transaction)
            mempool.delete()
            return True
        except ObjectDoesNotExist:
            return False
