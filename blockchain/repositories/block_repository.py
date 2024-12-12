from blockchain.models import Block
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum



class BlockRepository:
    @staticmethod
    def create(block_hash, validator, status, timestamp, epoch, slot, reward, difficulty, state_root, withdrawal_root, height, nonce):
        block = Block(
            block_hash=block_hash, validator=validator, status=status,
            timestamp=timestamp, epoch=epoch, slot=slot, reward=reward,
            difficulty=difficulty, state_root=state_root, withdrawal_root=withdrawal_root,
            height=height, nonce=nonce
        )
        block.save()
        return block

    @staticmethod
    def get_all():
        return Block.objects.all()

    @staticmethod
    def get_by_id(block_hash):
        try:
            return Block.objects.get(pk=block_hash)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update(block_hash, **kwargs):
        try:
            block = Block.objects.get(pk=block_hash)
            for key, value in kwargs.items():
                setattr(block, key, value)
            block.save()
            return block
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def delete(block_hash):
        try:
            block = Block.objects.get(pk=block_hash)
            block.delete()
            return True
        except ObjectDoesNotExist:
            return False


    @staticmethod
    def validator_block_statistics():
        """
        Агрегує дані про валідаторів і блоки:
        - Повертає сумарну винагороду для кожного валідатора, згруповану за статусом блоків.
        """
        return (
            Block.objects.values("validator__address", "status")
            .annotate(total_reward=Sum("reward"))
            .order_by("validator__address", "status")
        )