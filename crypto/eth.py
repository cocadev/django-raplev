import requests
import json

from cadmin import models
from .models import ETH
from django.utils.crypto import get_random_string
from .libs.etherscan.accounts import Account
from .libs.etherscan.blocks import Blocks
from .libs.etherscan.proxies import Proxies
from .libs.etherscan.tokens import Tokens
from .libs.etherscan.transactions import Transactions
from eth_account import Account as eaAccount
from django.core import serializers

ETHERSCAN_API_KEY = 'AH56YE6FZWX7QHMR6JFV3FGHCNWCXCVKCV'


class ETHProcessor:
    def __init__(self, customer):
        self.customer = customer#models.Customers.objects.get(id=1) #customer
        if self.customer.eth_wallet() is None:
            self.wallet_generation()
        self.password = self.customer.btc_wallet().password
        self.addr = self.customer.eth_wallet().addr
        self.account = Account(address=self.addr, api_key=ETHERSCAN_API_KEY)

    def wallet_generation(self, label = None):
        label = label if label is not None else self.customer.user.get_fullname() + ' wallet'
        user_password = get_random_string(60)
        acct = eaAccount.create(user_password)
        eth_wallet = ETH(
            id = acct.address,
            addr = acct.address,
            label = label,
            customer = self.customer,
            prv_key = acct.key.hex(),
            password = user_password
        )
        eth_wallet.save()
        return eth_wallet.__dict__

    def wallet_info(self):
        wallet = self.customer.eth_wallet()
        serialized_obj = serializers.serialize('json', [ wallet, ])
        return json.loads(serialized_obj)[0]['fields']

    def get_block_reward(self, block):
        api = Blocks(api_key=ETHERSCAN_API_KEY)
        reward_object = api.get_block_reward(block)
        return reward_object

    def get_balance(self):
        get_balance = float(self.account.get_balance())/1000000000000000000
        obj, created = models.Balance.objects.get_or_create(customer=self.customer, currency='ETH')
        obj.amount = get_balance
        obj.save()
        return get_balance

    def get_balance_multi(self):
        get_balances = self.account.get_balance_multiple()
        return get_balances

    def send_tx(self, target_addr, amount, prv_key = None):
        prv_key = prv_key if prv_key is not None else self.wallet_info()['prv_key']
        gasPrice = self.gas_price()
        txCount = self.get_transaction_count()
        transaction = {
            'to': target_addr,
            'value': int(amount * 1000000000000000000),
            'gas': 100000,
            'gasPrice': gasPrice,
            'nonce': txCount,   
            # 'chainId': 1
        }
        tx_hash = eaAccount.sign_transaction(transaction, prv_key)['rawTransaction'].hex()
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        payment = api.send_tx(tx_hash)
        return payment

    def get_most_recent_block(self):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        most_recent = int(api.get_most_recent_block(), 16)
        return most_recent

    def get_block_by_number(self, block_number):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        block = api.get_block_by_number(block_number)
        return block

    def get_uncle_by_blocknumber_index(self, block_number, uncle_index = 0):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        uncle = api.get_uncle_by_blocknumber_index(block_number, uncle_index)
        return uncle

    def get_block_transaction_count_by_number(self, block_number):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        tx_count = api.get_block_transaction_count_by_number(block_number)
        return tx_count

    def get_transaction_by_hash(self, tx_hash):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        tx = api.get_transaction_by_hash(tx_hash)
        return tx

    def get_transaction_by_blocknumber_index(self, block_number, tx_index = 0):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        tx = api.get_transaction_by_blocknumber_index(block_number, tx_index)
        return tx

    def get_transaction_count(self, tx_address=None):
        tx_address = tx_address if tx_address is not None else self.addr
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        tx_count = int(api.get_transaction_count(tx_address), 16)
        return tx_count

    def get_transaction_receipt(self, tx_hash):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        tx_receipt = api.get_transaction_receipt(tx_hash)
        return tx_receipt

    def get_code(self, code_address):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        code_contents = api.get_code(code_address)
        return code_contents

    def get_storage_at(self, storage_address, storage_pos = 0):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        storage_contents = api.get_storage_at(storage_address, storage_pos)
        return storage_contents

    def gas_price(self):
        api = Proxies(api_key=ETHERSCAN_API_KEY)
        price = int(api.gas_price(), 16)
        return price

    def get_token_supply(self):
        api = Tokens(contract_address=self.addr, api_key=ETHERSCAN_API_KEY)
        token_supply = api.get_total_supply()
        return token_supply

    def get_token_balance(self, addr):
        api = Tokens(contract_address=self.addr, api_key=ETHERSCAN_API_KEY)
        token_balance = api.get_token_balance(addr)
        return token_balance

    def get_status(self, tx):
        api = Transactions(api_key=ETHERSCAN_API_KEY)
        status = api.get_status(tx)
        return status

    def get_tx_receipt_status(self, tx):
        api = Transactions(api_key=ETHERSCAN_API_KEY)
        receipt_status = api.get_tx_receipt_status(tx)
        return receipt_status

    def get_block_reward(self, block):
        api = Blocks(api_key=ETHERSCAN_API_KEY)
        reward_object = api.get_block_reward(block)
        return reward_object

    def get_target_wallet_addr(self, customer=None, email=None):
        if customer is not None:
            return customer.eth_wallet().addr
        if email is not None:
            user = models.Users.objects.get(email=email)
            return user.customer().eth_wallet().addr
        return None