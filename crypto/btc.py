import requests
import json

from cadmin import models
from .models import BTC
from django.utils.crypto import get_random_string
from blockchain import createwallet, exchangerates, pushtx, statistics, blockexplorer
from blockchain.wallet import Wallet

NODE_WALLET_SERVICES = 'http://127.0.0.1:4001/'
API_CODE = '58ck39ajuiw'


class BTCProcessor:
    def __init__(self, customer):
        self.customer = customer#models.Customers.objects.get(id=1) #customer
        if self.customer.btc_wallet() is None:
            self.wallet_generation()
        self.password = self.customer.btc_wallet().password
        self.wallet_id = self.customer.btc_wallet().id
        self.wallet = Wallet(self.wallet_id, self.password, NODE_WALLET_SERVICES)

    def wallet_generation(self, label = None):
        label = label if label is not None else self.customer.user.get_fullname() + ' wallet'
        user_password = get_random_string(60)
        new_wallet = createwallet.create_wallet(user_password, API_CODE, NODE_WALLET_SERVICES, label = label)
        btc_wallet = BTC(
            id = new_wallet.identifier,
            addr = new_wallet.address,
            label = new_wallet.label,
            customer = self.customer,
            password = user_password
        )
        btc_wallet.save()
        return new_wallet.__dict__

    def wallet_info(self):
        wallet = self.wallet
        return wallet.__dict__

    def new_address(self, label = 'test_label'):
        newaddr = self.wallet.new_address(label)
        return newaddr

    def list_addresses(self):
        addresses = self.wallet.list_addresses()
        return addresses

    def get_balance(self):
        get_balance = float(self.wallet.get_balance()/100000000)
        obj, created = models.Balance.objects.get_or_create(customer=self.customer, currency='BTC')
        obj.amount = get_balance
        obj.save()
        return get_balance

    def send_tx(self, target_addr, amount, from_address = None):
        amount = amount*100000000
        payment = self.wallet.send(target_addr, amount, fee=500)#min fee=220
        return payment.__dict__['tx_hash']

    def send_many_tx(self, recipients):
        # recipients = { '1NAF7GbdyRg3miHNrw2bGxrd63tfMEmJob' : 1428300,
		# 		'1A8JiWcwvpY7tAopUkSnGuEYHmzGYfZPiq' : 234522117 }
        payment_many = self.wallet.send_many(recipients)
        return payment_many.tx_id

    def get_address(self, addr, confirmations = 2):
        addr = self.wallet.get_address(addr, confirmations = confirmations)
        return addr

    def archive_address(self, addr):
        archive_address = self.wallet.archive_address(addr)
        return archive_address

    def unarchive_address(self, addr):
        unarchive_address = self.wallet.unarchive_address(addr)
        return unarchive_address

    def push_tx(self, push_code):
        # push_code = '0100000001fd468e431cf5797b108e4d22724e1e055b3ecec59af4ef17b063afd36d3c5cf6010000008c4930460221009918eee8be186035be8ca573b7a4ef7bc672c59430785e5390cc375329a2099702210085b86387e3e15d68c847a1bdf786ed0fdbc87ab3b7c224f3c5490ac19ff4e756014104fe2cfcf0733e559cbf28d7b1489a673c0d7d6de8470d7ff3b272e7221afb051b777b5f879dd6a8908f459f950650319f0e83a5cf1d7c1dfadf6458f09a84ba80ffffffff01185d2033000000001976a9144be9a6a5f6fb75765145d9c54f1a4929e407d2ec88ac00000000'
        pushtxed = pushtx.pushtx(push_code)
        return pushtxed
        
    def get_price(self, currency, amount):
        btc_amount = exchangerates.to_btc(currency, amount)
        return btc_amount

    def statistics(self):
        stats = statistics.get()
        return stats

    def blockexplorer(self):
        block = blockexplorer.get_block('000000000000000016f9a2c3e0f4c1245ff24856a79c34806969f5084f410680')
        tx = blockexplorer.get_tx('d4af240386cdacab4ca666d178afc88280b620ae308ae8d2585e9ab8fc664a94')
        blocks = blockexplorer.get_block_height(2570)
        address = blockexplorer.get_address('1HS9RLmKvJ7D1ZYgfPExJZQZA1DMU3DEVd')
        xpub = None #blockexplorer.get_xpub('xpub6CmZamQcHw2TPtbGmJNEvRgfhLwitarvzFn3fBYEEkFTqztus7W7CNbf48Kxuj1bRRBmZPzQocB6qar9ay6buVkQk73ftKE1z4tt9cPHWRn')
        addresses = None # blockexplorer.get_multi_address('1HS9RLmKvJ7D1ZYgfPExJZQZA1DMU3DEVd', 'xpub6CmZamQcHw2TPtbGmJNEvRgfhLwitarvzFn3fBYEEkFTqztus7W7CNbf48Kxuj1bRRBmZPzQocB6qar9ay6buVkQk73ftKE1z4tt9cPHWRn')
        outs = blockexplorer.get_unspent_outputs('1HS9RLmKvJ7D1ZYgfPExJZQZA1DMU3DEVd')
        latest_block = blockexplorer.get_latest_block()
        txs = blockexplorer.get_unconfirmed_tx()
        blocks_by_name = None #blockexplorer.get_blocks(pool_name = 'Discus Fish')
    
    def get_target_wallet_addr(self, customer=None, email=None):
        if customer is not None:
            return customer.btc_wallet().addr
        if email is not None:
            user = models.Users.objects.get(email=email)
            return user.customer().btc_wallet().addr
        return None