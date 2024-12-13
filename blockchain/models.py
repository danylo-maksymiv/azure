from django.db import models


class Address(models.Model):
    address = models.CharField(max_length=40, primary_key=True, unique=True)
    eth_balance = models.DecimalField(max_digits=28, decimal_places=0, default=0)

    class Meta:
        # managed = False
        db_table = 'address'

    def __str__(self):
        return self.address


class Validator(models.Model):
    validator_id = models.AutoField(primary_key=True)
    address = models.OneToOneField(
        Address,
        related_name='validator_address',
        on_delete=models.CASCADE,
        to_field='address',
        db_column='address'
    )
    withdrawal_address = models.ForeignKey(
        Address,
        related_name='validator_withdrawal_address',
        on_delete=models.CASCADE,
        to_field='address',
        db_column='withdrawal_address'
    )
    eth_staked = models.DecimalField(max_digits=28, decimal_places=0)
    status = models.CharField(
        max_length=8,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        db_column='status',
    )
    slashed = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'validator'




class Block(models.Model):
    STATUS_CHOICES = [
        ('finalized', 'Finalized'),
        ('attested', 'Attested'),
        ('proposed', 'Proposed'),
        ('pending', 'Pending'),
        ('uncle', 'Uncle'),
        ('orphaned', 'Orphaned'),
        ('invalid', 'Invalid'),
    ]

    block_hash = models.CharField(max_length=64, primary_key=True, unique=True)
    validator = models.ForeignKey(
        Validator,
        on_delete=models.CASCADE,
        to_field='validator_id',
        db_column='validator_id',
        related_name='blocks'  # Додаємо related_name
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        db_column='status'
    )
    timestamp = models.DateTimeField()
    epoch = models.PositiveIntegerField()
    slot = models.PositiveIntegerField()
    reward = models.DecimalField(max_digits=28, decimal_places=0)
    difficulty = models.DecimalField(max_digits=28, decimal_places=0)
    state_root = models.CharField(max_length=64, unique=True)
    withdrawal_root = models.CharField(max_length=64)
    height = models.BigIntegerField()
    nonce = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'block'




class Transaction(models.Model):
    transaction_hash = models.CharField(max_length=64, primary_key=True, unique=True)
    from_address = models.ForeignKey(
        Address,
        related_name='from_address',
        on_delete=models.CASCADE,
        to_field='address',
        db_column='from_address'
    )
    to_address = models.ForeignKey(
        Address,
        related_name='to_address',
        on_delete=models.CASCADE,
        to_field='address',
        db_column='to_address'
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
        to_field='block_hash',
        db_column='block_hash',
        related_name='transactions'  # Додаємо related_name
    )

    class Meta:
        managed = False
        db_table = 'transaction'





class TransactionData(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('dropped', 'Dropped'),
        ('replaced', 'Replaced'),
    ]

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field='transaction_hash',
        db_column='transaction_hash'  # Вказуємо ім'я стовпця
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )
    value = models.DecimalField(max_digits=28, decimal_places=0)
    eth_price = models.FloatField()
    gas_limit = models.BigIntegerField()
    base_fee = models.DecimalField(max_digits=28, decimal_places=0)
    max_fee = models.DecimalField(max_digits=28, decimal_places=0)
    priority_fee = models.DecimalField(max_digits=28, decimal_places=0)
    input_data = models.TextField(null=True)
    timestamp = models.DateTimeField()
    gas_used = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'transaction_data'



class Contract(models.Model):
    contract_address = models.CharField(max_length=40, primary_key=True, unique=True)
    creator_address = models.ForeignKey(
        Address,
        related_name='contract_creator_address',
        on_delete=models.CASCADE,
        to_field='address',
        db_column='creator_address'  # Вказуємо ім'я стовпця
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        to_field='transaction_hash',
        db_column='transaction_hash'  # Вказуємо ім'я стовпця
    )

    class Meta:
        managed = False
        db_table = 'contract'



class ContractData(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field='contract_address',
        db_column='contract_address'  # Вказуємо ім'я стовпця
    )
    source_code = models.TextField()
    bytecode = models.TextField()
    name = models.CharField(max_length=255, null=True)
    version = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'contract_data'



class Token(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field='contract_address',
        db_column='contract_address'  # Вказуємо ім'я стовпця
    )
    symbol = models.CharField(max_length=255)
    supply = models.DecimalField(max_digits=65, decimal_places=0)
    decimals = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'token'



class Mempool(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        primary_key=True,
        to_field='transaction_hash',
        db_column='transaction_hash'  # Вказуємо ім'я стовпця
    )

    class Meta:
        managed = False
        db_table = 'mempool'


