from theme.constants import ESCROWS_STATUS_TYPES, VOTE_TYPES, TRADE_STATUS_TYPES, FLAT_CHOICES, CRYPTO_CHOICES, CURRENCY_CHOICES,REGISTRATION_CHOICES,CC_TYPES,LANGUAGE_CHOICES,TICKET_STATUS_CHOICES,TRADE_TYPES,CUSTOMER_TYPES,PAYMENT_METHODS,ROLE_TYPES,BOOLEAN_TYPES,STATUS_TYPES,VERIFIED_TYPES,PENDING_TYPES,ACCEPTIVE_TYPES,PAGESTATUS_TYPES,COUNTRY_CODE
from cadmin.models import Users, Pricing
from . import cache


def theme_decorators(request):

    cce = cache.CurrencyExchangeData()
    cce.generate()
    
    if 'set_country' in request.session:
        set_country = request.session['set_country']
    else:
        request.session['set_country'] = 'US'
        set_country = 'US'

    if 'set_csymbol' in request.session:
        set_csymbol = request.session['set_csymbol']
    else:
        request.session['set_csymbol'] = '$'
        set_csymbol = '$'

    if 'set_currency' in request.session:
        set_currency = request.session['set_currency']
    else:
        request.session['set_currency'] = 'USD'
        set_currency = 'USD'

    pricing = {
        'BTC_STRING': cce.get_price_rate_string("BTC", set_currency),
        'ETH_STRING': cce.get_price_rate_string("ETH", set_currency),
        'XRP_STRING': cce.get_price_rate_string("XRP", set_currency),
    } 

    return { 'pricing': pricing, 'theme_url': '', 'SET_COUNTRY': set_country, 'SET_CURRENCY': set_currency, 'SET_CSYMBOL': set_csymbol, **global_setting() }


def global_setting():
    return {"FLAT_CHOICES": FLAT_CHOICES, 
        "ESCROWS_STATUS_TYPES": ESCROWS_STATUS_TYPES, 
        "VOTE_TYPES": VOTE_TYPES, 
        "TRADE_STATUS_TYPES": TRADE_STATUS_TYPES, 
        "CRYPTO_CHOICES": CRYPTO_CHOICES, 
        "CURRENCY_CHOICES": CURRENCY_CHOICES, 
        "REGISTRATION_CHOICES": REGISTRATION_CHOICES, 
        "CC_TYPES": CC_TYPES, 
        "LANGUAGE_CHOICES": LANGUAGE_CHOICES, 
        "TICKET_STATUS_CHOICES": TICKET_STATUS_CHOICES, 
        "TRADE_TYPES": TRADE_TYPES, 
        "CUSTOMER_TYPES": CUSTOMER_TYPES, 
        "PAYMENT_METHODS": PAYMENT_METHODS, 
        "ROLE_TYPES": ROLE_TYPES, 
        "BOOLEAN_TYPES": BOOLEAN_TYPES, 
        "STATUS_TYPES": STATUS_TYPES, 
        "VERIFIED_TYPES": VERIFIED_TYPES, 
        "PENDING_TYPES": PENDING_TYPES, 
        "ACCEPTIVE_TYPES": ACCEPTIVE_TYPES, 
        "PAGESTATUS_TYPES": PAGESTATUS_TYPES, 
        "COUNTRY_CODE": COUNTRY_CODE}