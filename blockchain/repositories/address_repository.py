from blockchain.models import Address
from django.core.exceptions import ObjectDoesNotExist


class AddressRepository:
    @staticmethod
    def create(address,eth_balance):
        address_instance = Address(address=address,eth_balance=eth_balance)
        address_instance.save()
        return address_instance


    @staticmethod
    def get_all():
        return Address.objects.all()


    @staticmethod
    def get_by_id(address):
        try:
            return Address.objects.get(pk=address)
        except ObjectDoesNotExist:
            return None


    @staticmethod
    def update(address,**kwargs):
        try:
            address_instance = Address.objects.get(pk=address)
            for key, value in kwargs.items():
                setattr(address_instance, key, value)
            address_instance.save()
            return address_instance
        except ObjectDoesNotExist:
            return None


    @staticmethod
    def delete(address):
        try:
            address_instance = Address.objects.get(pk=address)
            address_instance.delete()
            return True
        except ObjectDoesNotExist:
            return False