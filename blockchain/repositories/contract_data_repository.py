from blockchain.models import ContractData
from django.core.exceptions import ObjectDoesNotExist


class ContractDataRepository:
    @staticmethod
    def create(contract, source_code, bytecode, name, version):
        contract_data = ContractData(contract=contract, source_code=source_code, bytecode=bytecode, name=name, version=version)
        contract_data.save()
        return contract_data

    @staticmethod
    def get_all():
        return ContractData.objects.all()

    @staticmethod
    def get_by_id(contract):
        try:
            return ContractData.objects.get(pk=contract)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update(contract, **kwargs):
        try:
            contract_data = ContractData.objects.get(pk=contract)
            for key, value in kwargs.items():
                setattr(contract_data, key, value)
            contract_data.save()
            return contract_data
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(contract):
        try:
            contract_data = ContractData.objects.get(pk=contract)
            contract_data.delete()
            return True
        except ObjectDoesNotExist:
            return False
