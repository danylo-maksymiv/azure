from blockchain.models import Token
from django.core.exceptions import ObjectDoesNotExist


class TokenRepository:
    @staticmethod
    def create(contract, symbol, supply, decimals, type):
        token = Token(contract=contract, symbol=symbol, supply=supply, decimals=decimals, type=type)
        token.save()
        return token

    @staticmethod
    def get_all():
        return Token.objects.all()

    @staticmethod
    def get_by_id(contract):
        try:
            return Token.objects.get(pk=contract)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update(contract, **kwargs):
        try:
            token = Token.objects.get(pk=contract)
            for key, value in kwargs.items():
                setattr(token, key, value)
            token.save()
            return token
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(contract):
        try:
            token = Token.objects.get(pk=contract)
            token.delete()
            return True
        except ObjectDoesNotExist:
            return False
