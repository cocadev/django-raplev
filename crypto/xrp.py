import requests
import json
from decimal import Decimal

from cadmin import models
from .models import XRP
from ripple_api import RippleRPCClient, Account
from ripple_api.utils import generate_seed

RIPPLE_SERVER = 'https://s1.ripple.com:51234/' # local
# RIPPLE_SERVER = 'http://r.ripple.com:51235/' # local
# RIPPLE_SERVER = 'http://s.altnet.rippletest.net:51235/' # testnet local
LOCAL_SERVER = 'http://localhost:5005'


class XRPProcessor:
    def __init__(self, customer):
        self.customer = customer
        self.client = RippleRPCClient(RIPPLE_SERVER)#, username='<username>', password='<password>'
        self.local = RippleRPCClient(LOCAL_SERVER)
        if self.customer.xrp_wallet() is None:
            self.wallet_generation()
        self.password = self.customer.xrp_wallet().password
        self.addr = self.customer.xrp_wallet().addr
        self.xrp_base = Decimal(1000000)

    def wallet_generation(self, label = None):
        label = label if label is not None else self.customer.user.get_fullname() + ' wallet'
        user_password = generate_seed('passphrase')
        acct = self.local.wallet_propose(passphrase = user_password)
        # acct = json.loads(requests.post('https://faucet.altnet.rippletest.net/accounts').content)['account']
        xrp_wallet = XRP(
            id = acct['account_id'],
            addr = acct['account_id'],
            label = label,
            customer = self.customer,
            password = user_password
        )
        xrp_wallet.save()
        return acct

    def wallet_info(self):
        account_info = self.client.account_info(self.addr)
        return account_info

    def get_balance(self):
        info = self.client.account_info(account=self.addr)
        balance = info.get('account_data', {}).get('Balance', 0)
        get_balance =  Decimal(balance) / self.xrp_base
        obj, created = models.Balance.objects.get_or_create(customer=self.customer, currency='XRP')
        obj.amount = get_balance
        obj.save()
        return get_balance

    def validation_create(self, secret="BAWL MAN JADE MOON DOVE GEM SON NOW HAD ADEN GLOW TIRE"):
        return self.local.validation_create(secret)

    def send_tx(self, target_addr, amount, currency = "USD", secret = None):
        secret = secret if secret is not None else self.password
        payment_json = dict(
            Account=self.addr,
            Amount=str(int(Decimal(amount) * self.xrp_base)),
            Destination=target_addr,
            TransactionType="Payment"
        )
        tx_hash = self.local.sign(payment_json, secret).get('tx_blob')
        payment = self.client.submit(tx_hash)
        return payment

    def account_lines(self):
        return self.client.account_lines(self.addr)

    def account_channels(self, destination_addr):
        return self.client.account_channels(self.addr, destination_addr)

    def account_currencies(self):
        return self.client.account_currencies(self.addr)

    def account_objects(self):
        return self.client.account_objects(self.addr)

    def account_offers(self):
        return self.client.account_offers(self.addr)

    def account_tx(self):
        return self.client.account_tx(self.addr)

    def gateway_balances(self):
        return self.client.gateway_balances(self.addr)

    def gateway_balances(self):
        return self.client.gateway_balances(self.addr)

    def noripple_check(self):
        return self.client.noripple_check(self.addr)

    def ledger(self):
        return self.client.ledger()

    def ledger_closed(self):
        return self.client.ledger_closed()

    def ledger_current(self):
        return self.client.ledger_current()

    def ledger_data(self, ledger_hash):
        return self.client.ledger_data(ledger_hash)

    def ledger_entry(self):
        return self.client.ledger_entry()

    def sign(self, tx_json, secret=""):
        return self.client.sign(tx_json, secret, True)

    def sign_for(self, account, seed, key_type, tx_json):
        return self.client.sign_for(self.addr, seed, key_type, tx_json)

    def submit(self, tx_blob):
        return self.client.ledger_current(tx_blob)

    def tx_history(self):
        return self.client.tx_history()

    # def get_balance_multi(self):
    #     get_balances = self.client.get_balance_multiple()
    #     return get_balances

    

    def tx_fee(self):
        return self.client.fee()

    def get_target_wallet_addr(self, customer=None, email=None):
        if customer is not None:
            return customer.xrp_wallet().addr
        if email is not None:
            user = models.Users.objects.get(email=email)
            return user.customer().xrp_wallet().addr
        return None