import redis
import json
import requests
from geopy import GoogleV3
from geopy.exc import GeocoderQueryError
import logging

from django.conf import settings


r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT
)

logger = logging.getLogger('raplev')
logger.setLevel(logging.INFO)
from cadmin.models import Pricing

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from forex_python.converter import CurrencyRates

class CurrencyExchangeData:
    """
    Class used for storing currency exchange rates for 10 minutes
    """

    def generate(self):
        # coinmarketcap = Market()
        current_rate_time = r.get('current_rate_time')
        try:
            if current_rate_time is None:
                self.set_pricing()
                r.set('current_rate_time', "Good")
                r.expire('current_rate_time', 600)
        except Exception as e:
            print(e)

    def get_price(self, crypto, flat, place='market_price'):
        current_rate = r.get(crypto+"-"+flat)
        if current_rate:
            return float("{:.3f}".format(float(current_rate)))
        else:
            return Pricing().get_price(crypto, flat, place)

    def get_rate(self, crypto, flat, place='market_price'):
        current_rate = r.get(crypto+"-"+flat+"-rate")
        if current_rate:
            return float("{:.3f}".format(float(current_rate)))
        else:
            return Pricing().get_rate(crypto, flat, place)
    
    def get_price_rate_string(self, crypto, flat):
        price = self.get_price(crypto, "USD")*self.get_price("USD", flat)
        rate = self.get_rate(crypto, "USD")*self.get_price("USD", flat)
        return '<span class="top-bar__value">' + str('{:.3f}'.format(price)) + ('</span><span class="top-bar__change is-positive"> +' if rate > 0 else '<span class="top-bar__change is-negative"> ') + str('{:.3f}'.format(rate)) + '%</span>'

    def set_pricing(self):
        data = self.get_market()
        for symbol in data['data']:
            crypto = data['data'][symbol]['symbol']
            flat = "USD"
            pricing = data['data'][symbol]
            price = pricing['quote'][flat]['price']
            rate = pricing['quote'][flat]['percent_change_1h']
            self.add_pricing(crypto, flat, price, rate)

        data = self.get_converter()
        for symbol in data:
            crypto = 'USD'
            flat = symbol
            price = data[symbol]
            if symbol in ['USD', 'EUR', 'GBP', 'JPY']:
                self.add_pricing(crypto, flat, price)
        
    def get_market(self):
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'id':'1,1027,52'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'b2f9d679-ed43-4973-a454-28b00c741b22',
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return e

    def get_converter(self):
        c = CurrencyRates()
        try:
            return c.get_rates('USD')
        except Exception as e:
            return e

    def add_pricing(self, crypto, flat, price, rate=0):
        Pricing(
            price_type = "market_price",
            crypto = crypto,
            flat = flat,
            price = price,
            rate = rate
        ).save()
        r.set(crypto+"-"+flat, price)
        r.expire(crypto+"-"+flat, 600)
        r.set(crypto+"-"+flat+"-rate", rate)
        r.expire(crypto+"-"+flat, 600)


class GoogleMapsGeocoding:
    """
    Class used for caching the values got from Google's geocoding service
    """

    def __init__(self):
        self.geo_locator = GoogleV3(api_key=settings.GOOGLE_API_KEY)

    def get_or_set_location(self, country, city, postcode):
        current_location = r.get('l-{country}-{city}-{postcode}'.format(country=country, city=city, postcode=postcode))
        if current_location:
            location = json.loads(current_location.decode())
            return location
        else:
            try:
                geo_location = self.geo_locator.geocode(components={
                    'country': country,
                    'locality': city,
                    'postal_code': postcode
                })
            except GeocoderQueryError as e:
                logger.error('Google Geocoding error: {}'.format(e))
                return None
            if geo_location:
                rgl = geo_location.raw
                r.set('l-{country}-{city}-{postcode}'.format(country=country, city=city, postcode=postcode),
                      json.dumps(rgl))
                r.expire('l-{country}-{city}-{postcode}'.format(country=country, city=city, postcode=postcode),
                         settings.GOOGLE_GEOCODING_CACHE_TIME)
                return rgl
            else:
                return None


class PhoneCodeCache:
    """
    Class used for temporarily storing the phone code used for authorizing the user
    """

    @staticmethod
    def set_phone_code(user_id):
        import random
        random.seed()
        phone_code = random.randint(10**(settings.SMS_CODE_LENGTH-1), 10**settings.SMS_CODE_LENGTH)
        r.set('phonecode-{}'.format(user_id), phone_code)
        r.expire('phonecode-{}'.format(user_id), 10)
        logger.info('Generated access code for user {user_id} - {phone_code}'.format(
            user_id=user_id, phone_code=phone_code))
        return phone_code

    @staticmethod
    def get_phone_code(user_id):
        if r.get('phonecode-{}'.format(user_id)):
            return r.get('phonecode-{}'.format(user_id)).decode()
        else:
            return None
