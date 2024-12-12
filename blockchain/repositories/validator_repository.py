from blockchain.models import Validator, Block, Transaction
from django.db.models import Sum, Count, DateField
from django.db.models.functions import TruncDate


class ValidatorRepository:
    @staticmethod
    def create(address, withdrawal_address, eth_staked, status, slashed):
        validator = Validator(
            address=address,
            withdrawal_address=withdrawal_address,
            eth_staked=eth_staked,
            status=status,
            slashed=slashed
        )
        validator.save()
        return validator

    @staticmethod
    def get_all():
        return Validator.objects.all()

    @staticmethod
    def get_by_id(validator_id):
        try:
            return Validator.objects.get(pk=validator_id)
        except Validator.DoesNotExist:
            return None

    @staticmethod
    def update(validator_id, **kwargs):
        try:
            validator = Validator.objects.get(pk=validator_id)
            for key, value in kwargs.items():
                setattr(validator, key, value)
            validator.save()
            return validator
        except Validator.DoesNotExist:
            return None

    @staticmethod
    def delete(validator_id):
        try:
            validator = Validator.objects.get(pk=validator_id)
            validator.delete()
            return True
        except Validator.DoesNotExist:
            return False

    @staticmethod
    def validator_block_statistics():
        """
        Повертає статистику блоків для валідаторів.
        """
        return (
            Validator.objects.annotate(
                total_reward=Sum('blocks__reward')  # Підрахунок винагороди за блоки
            )
            .values('address', 'status', 'total_reward')
            .filter(total_reward__isnull=False)  # Фільтруємо валідаторів із нульовою винагородою
        )

    @staticmethod
    def validator_transaction_statistics():
        from django.db.models.functions import TruncDate
        from django.db.models import Count

        return (
            Validator.objects
            .annotate(date=TruncDate('blocks__transactions__transactiondata__timestamp'))
            .values('address', 'date')
            .annotate(transactions=Count('blocks__transactions'))  # Рахуємо кількість транзакцій
            .order_by('date')
        )

