from blockchain.models import Contract
from django.core.exceptions import ObjectDoesNotExist


class ContractRepository:
    @staticmethod
    def create(contract_address, creator_address, transaction):
        contract = Contract(contract_address=contract_address, creator_address=creator_address, transaction=transaction)
        contract.save()
        return contract

    @staticmethod
    def get_all():
        return Contract.objects.all()

    @staticmethod
    def get_by_id(contract_address):
        try:
            return Contract.objects.get(pk=contract_address)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update(contract_address, **kwargs):
        try:
            contract = Contract.objects.get(pk=contract_address)
            for key, value in kwargs.items():
                setattr(contract, key, value)
            contract.save()
            return contract
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(contract_address):
        try:
            contract = Contract.objects.get(pk=contract_address)
            contract.delete()
            return True
        except ObjectDoesNotExist:
            return False
