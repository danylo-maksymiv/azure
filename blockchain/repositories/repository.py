from .address_repository import AddressRepository
from .validator_repository import ValidatorRepository
from .transaction_repository import TransactionRepository
from .transaction_data_repository import TransactionDataRepository
from .contract_repository import ContractRepository
from .contract_data_repository import ContractDataRepository
from .block_repository import BlockRepository
from .mempool_repository import MempoolRepository
from .token_repository import TokenRepository


class Repository:
    @staticmethod
    def address():
        return AddressRepository()

    @staticmethod
    def validator():
        return ValidatorRepository()

    @staticmethod
    def transaction():
        return TransactionRepository()

    @staticmethod
    def transaction_data():
        return TransactionDataRepository()

    @staticmethod
    def contract():
        return ContractRepository()

    @staticmethod
    def contract_data():
        return ContractDataRepository()

    @staticmethod
    def block():
        return BlockRepository()

    @staticmethod
    def mempool():
        return MempoolRepository()

    @staticmethod
    def token():
        return TokenRepository()

    @staticmethod
    def validator_block_statistics():
        return BlockRepository.validator_block_statistics()