from django import forms
from .models import *

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

class ValidatorForm(forms.ModelForm):
    class Meta:
        model = Validator
        fields = '__all__'

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionDataForm(forms.ModelForm):
    class Meta:
        model = TransactionData
        fields = '__all__'

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'

class ContractDataForm(forms.ModelForm):
    class Meta:
        model = ContractData
        fields = '__all__'

class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        fields = '__all__'

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = '__all__'

class MempoolForm(forms.ModelForm):
    class Meta:
        model = Mempool
        fields = '__all__'

