import logging
from datetime import datetime, timedelta

from django.utils.decorators import method_decorator

from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout, authenticate, login
from django.views import View
from django.shortcuts import render, redirect
from django.core import serializers
from django.template.loader import render_to_string

from cadmin import models
from .constants import CURRENCY_SYMBOL
from .decorators import customer_user_login_required, user_not_logged_in
from .context_processors import theme_decorators
from .cache import CurrencyExchangeData, GoogleMapsGeocoding
from django.template.defaulttags import register
from django.contrib.auth import (login as auth_login, logout as auth_logout)
import string, random

logger = logging.getLogger('raplev')
logger.setLevel(logging.INFO)
app_url = ''


@register.filter
def multiple3(num):    
    ret = True if num % 3 == 0 else False
    return ret


@register.filter
def cconv(price, flat):
    price = float(price) * CurrencyExchangeData().get_price("USD", flat)
    return "{:.3f}".format(price)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def current_user(request):
    try:
        # user = models.Users.objects.get(token=request.session['user'])
        # return user
        return request.user
    except:
        None


class Pages(View):
    
    def get(self, request, more={}):
        return render(request, 'theme/pages.html', {**more})


class SetCountry(View):
    
    def post(self, request, more={}):
        country_code = request.POST.get('language')
        request.session['set_country'] = country_code
        request.session['set_currency'] = CURRENCY_SYMBOL[country_code]['currency'] if country_code in CURRENCY_SYMBOL else 'USD'
        request.session['set_csymbol'] = CURRENCY_SYMBOL[country_code]['csymbol'] if country_code in CURRENCY_SYMBOL else '$'
        return redirect('/')


def get_set_country(request):
    try:
        return request.session['set_country']
    except: 
        return 'US'


def get_permission_value(request, column):
    if column == 'identified_user_required':
        try:
            return request.user.id_verified
        except:
            return False
    if column == 'sms_verification_required':
        try:
            return request.user.phone_verified
        except:
            return False
    if column == 'minimum_successful_trades':
        try:
            return request.user.customer().successful_trade_count()
        except:
            return 0
    if column == 'minimum_complete_trade_rate':
        try:
            return request.user.customer().successful_trade_rate()
        except:
            return 0


class Index(View):
    
    def get(self, request, more={}):
        crypto_filter = request.GET.get('crypto_filter', '')
        type_all = ['buy'] if  request.GET.get('crypto_all_buy', 'no') == 'on' else []
        type_all.append('sell' if request.GET.get('crypto_all_sell', 'no') == 'on' else 'nooooo')

        types = {}
        items = {}
        for item in ['BTC', 'ETH', 'XRP']:
            types[item] = ['buy'] if  request.GET.get('crypto_'+item+'_buy', 'no') == 'on' else []
            types[item].append('sell' if request.GET.get('crypto_'+item+'_sell', 'no') == 'on' else 'nooooo')

            if crypto_filter == 'true':
                items.update({item: models.Offers.objects.filter(Q(what_crypto=item, admin_confirmed=True, supported_location__icontains=get_set_country(request)),
                    # Q(Q(identified_user_required=get_permission_value(request, 'identified_user_required')) | Q(identified_user_required=False)),
                    # Q(Q(sms_verification_required=get_permission_value(request, 'sms_verification_required')) | Q(sms_verification_required=False)),
                    # Q(minimum_successful_trades__lte=get_permission_value(request, 'minimum_successful_trades')),
                    # Q(minimum_complete_trade_rate__lte=get_permission_value(request, 'minimum_complete_trade_rate')),
                    Q(Q(trade_type__in=types[item]) | Q(trade_type__in=type_all))).order_by('-created_at')[:5]})
            else:
                items.update({item: models.Offers.objects.filter(Q(what_crypto=item, admin_confirmed=True, supported_location__icontains=get_set_country(request)),
                    # Q(Q(identified_user_required=get_permission_value(request, 'identified_user_required')) | Q(identified_user_required=False)),
                    # Q(Q(sms_verification_required=get_permission_value(request, 'sms_verification_required')) | Q(sms_verification_required=False)),
                    # Q(minimum_successful_trades__lte=get_permission_value(request, 'minimum_successful_trades')),
                    # Q(minimum_complete_trade_rate__lte=get_permission_value(request, 'minimum_complete_trade_rate'))
                    ).order_by('-created_at')[:5]})


        crypto_all_buy = True if request.GET.get('crypto_all_buy', 'no') == 'on' else False
        crypto_BTC_buy = True if request.GET.get('crypto_BTC_buy', 'no') == 'on' else False
        crypto_ETH_buy = True if request.GET.get('crypto_ETH_buy', 'no') == 'on' else False
        crypto_XRP_buy = True if request.GET.get('crypto_XRP_buy', 'no') == 'on' else False

        crypto_all_sell = True if request.GET.get('crypto_all_sell', 'no') == 'on' else False
        crypto_BTC_sell = True if request.GET.get('crypto_BTC_sell', 'no') == 'on' else False
        crypto_ETH_sell = True if request.GET.get('crypto_ETH_sell', 'no') == 'on' else False
        crypto_XRP_sell = True if request.GET.get('crypto_XRP_sell', 'no') == 'on' else False

        return render(request, 'theme/index.html', {'BTC_items': items['BTC'], 'ETH_items': items['ETH'], 'XRP_items': items['XRP'], 
            'crypto_all_buy': crypto_all_buy, 'crypto_all_sell': crypto_all_sell, 
            'crypto_BTC_buy': crypto_BTC_buy, 'crypto_BTC_sell': crypto_BTC_sell, 
            'crypto_ETH_buy': crypto_ETH_buy, 'crypto_ETH_sell': crypto_ETH_sell, 
            'crypto_XRP_buy': crypto_XRP_buy, 'crypto_XRP_sell': crypto_XRP_sell, 
            **more})


@method_decorator(user_not_logged_in, name='dispatch')
class Login(View):

    def get(self, request, more={}):
        next_to = more['next'] if 'next' in more else request.GET.get('next', '').strip()
        return render(request, 'theme/login.html', {'next': next_to, **more})

    def post(self, request):
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        next_to = request.POST.get('next', '').strip()

        try:
            user = models.Users.objects.get(Q(email=email_or_username))# | Q(username=email_or_username)
            if user and check_password(password, user.password) and user.is_customer:
                token = user.token if user.token else get_random_string(length=100)
                user.token = token
                user.save()
                models.LoginLogs(
                    user=user,
                    ip_address=get_client_ip(request)
                ).save()
                auth_login(request, user)
                # request.session['user'] = token
            else:
                try:
                    models.SecurityStatus(
                        user=user,
                        ip_address=get_client_ip(request)
                    ).save()
                except:
                    log = 'here it need to sys log for error user login.'
                if next_to:
                    return self.get(request, {'next': next_to, 'error': {'password': 'Incorrect Password'}})
                else:
                    return JsonResponse({'error': {'password': 'Incorrect Password'}})
        except Exception as e:
            if next_to:
                return self.get(request, {'next': next_to, 'error': {'email': 'Incorrect User'}})
            else:
                return JsonResponse({'error': {'email': 'Incorrect User'}})
        
        if next_to:
            return redirect(next_to)
        else:
            return JsonResponse({'success': True})


@customer_user_login_required
def logout(request):
    # del request.session['user']
    auth_logout(request)
    # request.session['global_alert'] = {'success': "You are logged out."}
    return redirect('/'+app_url+'')


@customer_user_login_required
def get_badges(request):
    received_offers = models.Trades.objects.filter(Q(offer__created_by=current_user(request).customer(), status__in=['counting', 'accepted']) | 
            Q(vendor=current_user(request).customer(), status__in=['accepted'])).count()
    transactions = models.Trades.objects.filter(
        Q(Q(offer__created_by=current_user(request).customer()) | Q(vendor=current_user(request).customer()), Q(status__in=['waiting', 'archived'])) | 
        Q(status='accepted', vendor=current_user(request).customer())).count()
    messages = models.Messages.objects.filter(partner=current_user(request), readed=False).count()
    return JsonResponse({'received_offers': received_offers, 'transactions': transactions, 'messages': messages})


@method_decorator(user_not_logged_in, name='dispatch')
class Register(View):

    def get(self, request, more={}):
        next_to = more['next'] if 'next' in more else request.GET.get('next', '').strip()
        return render(request, 'theme/register.html', {'next': next_to, **more})

    def post(self, request):
        customer_type = request.POST.get('customer_type', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        next_to = request.POST.get('next', '').strip()

        if password != password_confirm:
            if next_to:
                return self.get(request, {'next': next_to, 'error': {'password': 'Password is not confirmed.'}})
            else:
                return JsonResponse({'error': {'password': 'Password is not confirmed.'}})
        try:
            user = models.Users.objects.filter(Q(email=email) | Q(username=username))
            if user:
                if next_to:
                    return self.get(request, {'next': next_to, 'error': {'email': 'This account is already exist.'}})
                else:
                    return JsonResponse({'error': {'email': 'This account is already exist.'}})
            user = models.Users(
                username=username,
                email=email,
                password=make_password(password),
                date_joined=datetime.now(),
                is_customer=True
            )
            user.save()
            customer = models.Customers(
                user = user,
                customer_type = customer_type,
                seller_level = 1# if customer_type == 'sell' else None
            )
            customer.save()
            token = user.token if user.token else get_random_string(length=100)
            user.token = token
            user.save()
            auth_login(request, user)
            # request.session['user'] = token

        except Exception as e:
            if next_to:
                return self.get(request, {'next': next_to, 'error': {'email': 'Something wrong. Please try later.'}})
            else:
                return JsonResponse({'error': {'email': 'Something wrong. Please try later.'}})
        
        if next_to:
            return redirect(next_to)
        else:
            return JsonResponse({'success': True})


@method_decorator(user_not_logged_in, name='dispatch')
class ForgotPassword(View):

    def post(self, request):
        email = request.POST.get('email', '').strip()
        phonenumber = request.POST.get('phonenumber', '').strip()
        next_to = request.POST.get('next', '').strip()

        try:
            users = models.Users.objects.filter(Q(email=email) | Q(phonenumber=phonenumber))
            if users.count() > 0:
                user = users[0]
            else:
                if email:
                    if next_to:
                        return ForgotPasswordEmail.get(ForgotPasswordEmail, request, {'error': {'email': 'Please Insert correct Email.'}, 'next': next_to})
                    else:
                        return JsonResponse({'error': {'email': 'Please Insert correct Email.'}})
                elif phonenumber:
                    if next_to:
                        return ForgotPasswordPhone.get(ForgotPasswordPhone, request, {'error': {'phonenumber': 'Please Insert correct Phone number.'}, 'next': next_to})
                    else:
                        return JsonResponse({'error': {'phonenumber': 'Please Insert correct Phonenumber.'}})

            if email:
                next_tos = '&next='+next_to if next_to else ''
                user.send_forgot_pw_email(next_tos)
                if next_to:
                    return ForgotPasswordEmail.get(ForgotPasswordEmail, request, {'alert': {'success': 'Verification Email sent to your email, Please check your emails.'}, 'next': next_to})
                else:
                    return JsonResponse({'success': 'Verification Email sent to your email, Please check your emails.'})
            elif phonenumber:
                if not user.send_phone_code(phonenumber):
                    if next_to:
                        return ForgotPasswordPhone.get(ForgotPasswordPhone, request, {'error': {'phonenumber': 'Please Insert correct Phone number.'}, 'next': next_to})
                    else:
                        return JsonResponse({'error': {'phonenumber': 'Please Insert correct Phonenumber.'}})
                if next_to:
                    return redirect(app_url+'/confirm-forgot-password-phone-code?phonenumber='+phonenumber+'&next='+next_to)
                else:
                    return JsonResponse({'phone_code_confirm': True, 'phonenumber': phonenumber})
            else:
                return {'error': 'Insert Email or Phonenumber'}
        except Exception as e:
            print(e)
            return JsonResponse({'error': True})
        
        if next_to:
            return redirect(next_to)
        else:
            return JsonResponse({'success': True})


@method_decorator(user_not_logged_in, name='dispatch')
class ForgotPasswordEmail(View):

    def get(self, request, more={}):
        next_to = more['next'] if 'next' in more else request.GET.get('next', '').strip()
        return render(request, 'theme/forgot-password-email.html', {'next': next_to, **more})


@method_decorator(user_not_logged_in, name='dispatch')
class ForgotPasswordPhone(View):

    def get(self, request, more={}):
        next_to = more['next'] if 'next' in more else request.GET.get('next', '').strip()
        return render(request, 'theme/forgot-password-phone.html', {'next': next_to, **more})


@method_decorator(user_not_logged_in, name='dispatch')
class ResendConfirmEmail(View):
    
    def post(self, request):
        user = current_user(request)
        user.send_confirm_email()
        return JsonResponse({'success': 'Email sent.'})


@method_decorator(user_not_logged_in, name='dispatch')
class ResendConfirmPhone(View):
    
    def post(self, request):
        phonenumber = request.POST.get('phonenumber', '')
        try:
            user = models.Users.objects.get(phonenumber=phonenumber)
            if not user.send_phone_code(phonenumber):
                return JsonResponse({'error': 'Try again.'})

            return JsonResponse({'success': 'Phone code resent.'})
        except:
            return JsonResponse({'error': 'Try again.'})


@method_decorator(user_not_logged_in, name='dispatch')
class ConfirmForgotPWPhoneCode(View):

    def get(self, request, more={}):
        next_to = more['next'] if 'next' in more else request.GET.get('next', '').strip()
        phonenumber = request.GET.get('phonenumber', '').strip()
        return render(request, 'theme/confirm-forgot-password-phone-code.html', {'next': next_to, 'phonenumber': phonenumber, **more})

    def post(self, request):
        phonenumber = request.POST.get('phonenumber', '')
        code = request.POST.get('code', '')
        next_to = request.POST.get('next', '').strip()
        try:
            user = models.Users.objects.get(phonenumber=phonenumber)
            if True:#user.validate_phone_code(phonenumber, code):
                user.phone_verified = True
                user.phonenumber = phonenumber
                user.save()
                auth_login(request, user)
                # request.session['user'] = user.token
                if next_to:
                    return redirect(app_url+'/reset-password?next='+next_to)
                else:
                    return JsonResponse({'success': True})
            else:
                if next_to:
                    return self.get(request, {'next': next_to, 'phonenumber': phonenumber, 'error': {'code': 'Invaild phone code. Try again'}})
                else:
                    return JsonResponse({'error': 'That`s invalid phone code.'})
        except:
            if next_to:
                return self.get(request, {'next': next_to, 'phonenumber': phonenumber, 'error': {'code': 'ERROR!. Try again'}})
            else:
                return JsonResponse({'error': 'Try again.'})

class ConfirmForgotPWEmail(View):

    def get(self, request, more={}):
        token = request.GET.get('t', '').strip()
        next_to = request.GET.get('next', '').strip()
        try:
            user = models.Users.objects.get(token=token)
            user.email_verified = True
            user.save()
            auth_login(request, user)
            # request.session['user'] = user.token
        
            if next_to:
                return redirect(app_url+'/reset-password?next='+next_to)
            else:
                return Index.get(Index, request, {'alert': {'success': 'Email Confirmed'}})
        except:
            return Index.get(Index, request, {'alert': {'success':  'Email is Not Verified'}})


class ConfirmForgotPWPhone(View):

    def post(self, request):
        return False

@method_decorator(customer_user_login_required, name='dispatch')
class ResetPassword(View):

    def get(self, request, more={}):
        next_to = more['next'] if 'next' in more else request.GET.get('next', '').strip()
        return render(request, 'theme/reset-password.html', {'next': next_to, **more})

    def post(self, request):
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        next_to = request.POST.get('next', '/')
        if password != password_confirm:
            return self.get(request, {'next': next_to, 'error': {'password': 'Password is not confirmed.'}})
        try:
            user = current_user(request)
            user.password = make_password(password)
            user.save()
            return redirect(next_to)
        except:
            return self.get(request, {'next': next_to, 'alert': {'warning': 'Error! Try later.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class ResendVerifyEmail(View):

    def post(self, request):
        user = current_user(request)
        user.send_confirm_email()
        return JsonResponse({'success': 'Email sent.'})


@method_decorator(customer_user_login_required, name='dispatch')
class ResendVerifyPhone(View):

    def post(self, request):
        phonenumber = request.POST.get('phonenumber', '')
        user = current_user(request)
        if models.Users.objects.filter(~Q(id=user.id), Q(phonenumber=phonenumber, phone_verified=True)).count() > 0:
            return JsonResponse({'error': True})
        # if not user.send_phone_code(phonenumber):
        #     return JsonResponse({'error': True})
        return JsonResponse({'success': True})


@method_decorator(customer_user_login_required, name='dispatch')
class VerifyPhoneCode(View):

    def get(self, request, more={}):
        return render(request, 'theme/index.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class VerifyEmail(View):

    def get(self, request, more={}):
        token = request.GET.get('t', '').strip()
        next_to = request.GET.get('next', '').strip()
        try:
            user = current_user(request)

            if token == user.token:
                user.email_verified = True
                user.save()
                if next_to:
                    return redirect(next_to)
                else:
                    return Index.get(Index, request, {'alert': {'success': 'Email Verified'}})
            else:
                return Index.get(request, {'alert': 'Email is Not Verified'})

        except:
            return Index.get(request, {'alert': 'Email is Not Verified'})


@method_decorator(customer_user_login_required, name='dispatch')
class VerifyPhone(View):

    def post(self, request, more={}):
        phonenumber = request.POST.get('phonenumber', '')
        code = request.POST.get('code', '')
        try:
            user = current_user(request)
            if not user.validate_phone_code(phonenumber, code):
                return JsonResponse({'error': 'That`s invalid phone code.'})
            user.phone_verified = True
            user.phonenumber = phonenumber
            user.save()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'error': 'Try again.'})


@method_decorator(customer_user_login_required, name='dispatch')
class NewOffer(View):
    
    def get(self, request, more={}):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Offers.objects.get(id=item_id) if item_id else ''
        return render(request, 'theme/new-offer.html', {'item': item, **more})

    def post(self, request):
        item_id = request.POST.get('item_id', '')
        trade_price = float(request.POST.get('trade_price', 0))
        if request.POST.get('useMarketPrice', '').strip() == 'on':
            trade_price = CurrencyExchangeData().get_price(request.POST.get('what_crypto'), request.POST.get('flat'), 'market_price')
        if request.POST.get('trailMarketPrice', '').strip() == 'on':
            trade_price = CurrencyExchangeData().get_price(request.POST.get('what_crypto'), request.POST.get('flat'), 'trail_market_price')

        object_data = {
            'trade_type': request.POST.get('trade_type'),
            'what_crypto': request.POST.get('what_crypto'),
            'flat': request.POST.get('flat'),
            'postal_code': request.POST.get('postal_code') if request.POST.get('postal_code') else None,
            'show_postcode': True if request.POST.get('show_postcode') == 'on' else False,
            'country': request.POST.get('country'),
            'city': request.POST.get('city'),
            'trade_price': trade_price,
            'use_market_price': True if request.POST.get('useMarketPrice') == 'on' else False,
            'trail_market_price': True if request.POST.get('trailMarketPrice') == 'on' else False,
            'profit_start': float(request.POST.get('profit_start')) if request.POST.get('profit_start', None) != '' else None,
            'profit_end': float(request.POST.get('profit_end')) if request.POST.get('profit_end', None) != '' else None,
            'profit_time': request.POST.get('profit_time'),
            'minimum_transaction_limit': request.POST.get('minimum_transaction_limit'),
            'maximum_transaction_limit': request.POST.get('maximum_transaction_limit'),
            'operating_hours_start': request.POST.get('operating_hours_start'),
            'operating_hours_end': request.POST.get('operating_hours_end'),
            'restrict_hours_start': request.POST.get('restrict_hours_start'),
            'restrict_hours_end': request.POST.get('restrict_hours_end'),
            'proof_times': request.POST.get('proof_times'),
            'supported_location': request.POST.getlist('supported_location[]') if request.POST.getlist('supported_location[]') else ['US'],
            'trade_overview': request.POST.get('trade_overview', '').strip(),
            'message_for_proof': request.POST.get('message_for_proof', '').strip(),
            'identified_user_required': True if request.POST.get('identified_user_required') == 'on' else False,
            'sms_verification_required': True if request.POST.get('sms_verification_required') == 'on' else False,
            'minimum_successful_trades': request.POST.get('minimum_successful_trades'),
            'minimum_complete_trade_rate': request.POST.get('minimum_complete_trade_rate'),
            'admin_confirmed': True,#False
            'created_at': datetime.now(),
        }

        offer = models.Offers()
        try:
            offer.__dict__.update(object_data)
            offer.created_by = current_user(request).customer()
            offer.save()
            return OfferActivity.get(OfferActivity, request, {'item_id': offer.pk, 'offer_success': 'Offer Posted'})
        except Exception as e:
            print(e)
            return self.get(request, {'alert': {'warning': 'Sorry, Your offer is not saved.'}})


class SupportCenter(View):

    def get(self, request, more={}):
        # items = models.Tickets.objects.filter('email' == current_user(request).email)[:100]
        items = models.Tickets.objects.all().order_by('created_at')[:100]
        return render(request, 'theme/support-center.html', {'items': items, **more})


class SubmitTicket(View):

    def get(self, request, more={}):
        return render(request, 'theme/submit-ticket.html', {**more})

    def post(self, request):
        object_data = {
            'email': request.POST.get('email', ''),
            'topic': request.POST.get('topic', ''),
            'content': request.POST.get('content', ''),
            'attached_files': request.POST.get('attached_files', ''),
            'created_at': datetime.now(),
            'transaction': None,
            'is_dispute': False,
            'ticket_manager': current_user(request) if current_user(request) else None,
            'ticket_priority': 'Low'
        }
        ticket = models.Tickets()
        ticket.__dict__.update(object_data)
        ticket.save()
        return self.get(request, {'alert': {'success': 'Submit ticket success!!'}})

class TicketDetails(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Tickets.objects.get(id=item_id)
        return render(request, 'theme/ticket-details.html', {'item': item, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class ProfileOverview(View):

    def get(self, request, more={}):
        return render(request, 'theme/profile-overview.html', {**more})

    def post(self, request):
        password_old = request.POST.get('password_old', '')
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        avatars = request.POST.get('avatar', '')
        object_data = {
            'email': request.POST.get('email', ''),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'billing_address': request.POST.get('billing_address', ''),
            'overview': request.POST.get('overview', ''),
            'phonenumber': request.POST.get('phonenumber', ''),
        }
        user = current_user(request)
        user.__dict__.update(object_data)

        # set 2 factor authentication
        if request.POST.get('use_2factor_authentication') == 'on' and not user.phone_verified:
            return self.get(request, {'error': {'phonenumber': 'Verify your phone before setting 2 factor authentication.'}})
        else:
            user.use_2factor_authentication= True if request.POST.get('use_2factor_authentication') == 'on' else False

        # update password through checking old password
        if password and check_password(password_old, user.password) and password == password_confirm:
            user.password = make_password(password)
        elif password != '':
            return self.get(request, {'error': {'password_old': 'Incorrect Password!'}})

        # set avatar
        lists = avatars.split(',') if avatars else []
        if len(lists) > 0:
            # print(lists)
            avatar = models.Medias.objects.get(id=lists[-1])
            user.avatar = avatar

        user.save()
        return self.get(request, {'alert': {'success': 'Profile updated successfully!'}})

@method_decorator(customer_user_login_required, name='dispatch')
class ReceivedOffers(View):

    def get(self, request, more={}):
        loadmore = request.GET.getlist('loadmore[]', [])
        items = models.Trades.objects.filter(
            Q(offer__created_by=current_user(request).customer(), status__in=['counting', 'accepted']) | 
            Q(vendor=current_user(request).customer(), status__in=['accepted']), 
            ~Q(id__in=loadmore)
            ).order_by('-created_at')[:3]
        if loadmore:
            return render(request, 'theme/received-offers-more.html', {'items': items})
        return render(request, 'theme/received-offers.html', {'items': items, **more})

    def post(self, request):
        item_id = request.POST.get('item_id', '')
        mode = request.POST.get('mode', '')
        try:
            item = models.Trades.objects.get(id=item_id)
            item.status = mode
            item.save()
            
            if mode == 'accepted':
                userrel1, created3 = models.UserRelations.objects.get_or_create(user=trade.buyer().user, partner=trade.seller().user, defaults={'created_at': datetime.now()})
                userrel2, created4 = models.UserRelations.objects.get_or_create(user=trade.seller().user, partner=trade.buyer().user, defaults={'created_at': datetime.now()})
            return JsonResponse({'success': mode+'!'})
        except:
            return JsonResponse({'error': 'Error! Try again.'})

@method_decorator(customer_user_login_required, name='dispatch')
class BuySellCoins(View):

    def get(self, request, more={}):
        return redirect(app_url+'/withdrawals')


@method_decorator(customer_user_login_required, name='dispatch')
class Funding(View):

    def get(self, request, more={}):
        currency = request.GET.get('currency', '')
        return render(request, 'theme/fund.html', {'currency': currency, **more})

    def post(self, request):
        mode = request.POST.get('mode', '')
        if mode == 'add_card':
            card_name = request.POST.get('card_name', '')
            card_number = request.POST.get('card_number', '')
            security_code = request.POST.get('security_code', '')
            expiration_date = request.POST.get('expiration_date', '')
            # [[[?]]] require checking bankcard
            try:
                try:
                    exist = models.UserIDs.objects.get(user=current_user(request), card_name=card_name)
                    return self.get(request, {'alert': {'warning': 'Already, Inserted.'}})
                except:
                    card = models.UserIDs()
                    card.card_name = card_name
                    card.card_number = card_number
                    card.security_code = security_code
                    card.expiration_date = expiration_date
                    card.user = current_user(request)
                    card.save()
                    return self.get(request, {'alert': {'success': 'Created card'}})
            except Exception as e:
                print(e)
                return self.get(request, {'alert': {'warning': 'Not created. Try again.'}})

        if mode == 'remove_card':
            item_id = request.POST.get('item_id', '')
            try:
                card = models.UserIDs.objects.get(id=item_id)
                card.delete()
                return self.get(request, {'alert': {'success': 'Card deleted.'}})
            except:
                return self.get(request, {'alert': {'warning': 'Try again.'}})

        if mode == 'fund':
            fund_crypto = request.POST.get('fund_crypto', '')
            amount = request.POST.get('amount', '')
            card_id = request.POST.get('card', '')
            # [[[?]]]get money from card.
            try:
                obj, created = models.Balance.objects.get_or_create(customer=current_user(request).customer(), currency=fund_crypto)
                obj.amount = float(amount) + obj.amount
                obj.save()
                card = models.UserIDs.objects.get(id=card_id)
                drawlist = models.DrawLists()
                drawlist.draw_type = 'fund'
                drawlist.amount = float(amount)
                drawlist.currency = fund_crypto
                drawlist.card = card
                drawlist.details = 'Fund from ' + card.card_name
                drawlist.created_by = current_user(request).customer()
                drawlist.save()
                return self.get(request, {'alert': {'success': amount+' '+fund_crypto+' Funded.'}})
            except Exception as e:
                print(e)
                return self.get(request, {'alert': {'warning': 'Try again.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class UserPublicProfile(View):

    def get(self, request, more={}):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Customers.objects.get(id=item_id)
        items = models.Offers.objects.filter(created_by=item, is_expired=False)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/user-public-profile/?'
        return render(request, 'theme/user-public-profile.html', {'customer': item, 'items': items, 'paginator' : paginator, 'base_url': base_url,  **more})


@method_decorator(customer_user_login_required, name='dispatch')
class OfferActivity(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Offers.objects.get(id=item_id)
        return render(request, 'theme/offer-activity.html', {'item': item, **more})

    def post(self, request):
        item_id = request.POST.get('item_id', '')
        item = models.Offers.objects.get(id=item_id)
        item.is_paused = not item.is_paused
        item.paused_by = current_user(request) if item.is_paused else None
        item.save()
        offer_success = 'Your Offer is resumed by moderator.' if not item.is_paused else False
        offer_error = 'Your Offer is paused by moderator.' if item.is_paused else False
        return self.get(request, {'item_id': item_id, 'offer_error': offer_error, 'offer_success': offer_success })


@method_decorator(customer_user_login_required, name='dispatch')
class EditOffer(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Offers.objects.get(id=item_id)
        if item.created_by == current_user(request).customer():
            return render(request, 'theme/edit-offer.html', {'item': item, **more})
        else:
            return redirect(app_url)

    def post(self, request):
        item_id = request.POST.get('item_id', '')
        trade_price = float(request.POST.get('trade_price', 0))
        if request.POST.get('useMarketPrice', '').strip() == 'on':
            trade_price = CurrencyExchangeData().get_price(request.POST.get('what_crypto'), request.POST.get('flat'), 'market_price')
        if request.POST.get('trailMarketPrice', '').strip() == 'on':
            trade_price = CurrencyExchangeData().get_price(request.POST.get('what_crypto'), request.POST.get('flat'), 'trail_market_price')

        object_data = {
            'trade_type': request.POST.get('trade_type'),
            'what_crypto': request.POST.get('what_crypto'),
            'flat': request.POST.get('flat'),
            'postal_code': request.POST.get('postal_code') if request.POST.get('postal_code') else None,
            'show_postcode': True if request.POST.get('show_postcode') == 'on' else False,
            'country': request.POST.get('country'),
            'city': request.POST.get('city'),
            'trade_price': trade_price,
            'use_market_price': True if request.POST.get('useMarketPrice') == 'on' else False,
            'trail_market_price': True if request.POST.get('trailMarketPrice') == 'on' else False,
            'profit_start': float(request.POST.get('profit_start')) if request.POST.get('profit_start', '') != '' else None,
            'profit_end': float(request.POST.get('profit_end')) if request.POST.get('profit_end', '') != '' else None,
            'profit_time': request.POST.get('profit_time'),
            'minimum_transaction_limit': request.POST.get('minimum_transaction_limit'),
            'maximum_transaction_limit': request.POST.get('maximum_transaction_limit'),
            'operating_hours_start': request.POST.get('operating_hours_start'),
            'operating_hours_end': request.POST.get('operating_hours_end'),
            'restrict_hours_start': request.POST.get('restrict_hours_start'),
            'restrict_hours_end': request.POST.get('restrict_hours_end'),
            'proof_times': request.POST.get('proof_times'),
            'supported_location': request.POST.getlist('supported_location[]'),
            'trade_overview': request.POST.get('trade_overview', '').strip(),
            'message_for_proof': request.POST.get('message_for_proof', '').strip(),
            'identified_user_required': True if request.POST.get('identified_user_required') == 'on' else False,
            'sms_verification_required': True if request.POST.get('sms_verification_required') == 'on' else False,
            'minimum_successful_trades': request.POST.get('minimum_successful_trades'),
            'minimum_complete_trade_rate': request.POST.get('minimum_complete_trade_rate'),
            'admin_confirmed': False,
            'created_at': datetime.now(),
        }
        try:
            offer = models.Offers.objects.get(id=item_id)
            offer.__dict__.update(object_data)
            offer.created_by = current_user(request).customer()
            offer.save()
            return OfferActivity.get(OfferActivity, request, {'item_id': offer.pk, 'offer_success': 'Offer Posted'})
        except Exception as e:
            print(e)
            return OfferActivity.get(OfferActivity, request, {'item_id': offer.pk, 'offer_error': 'Your Offer is not running. Ref: RD23. <a href="'+app_url+'/issue?name=RD23">Find out</a> what it means'})


@method_decorator(customer_user_login_required, name='dispatch')
class AllOffers(View):

    def get(self, request, more={}):
        items = models.Offers.objects.order_by('-created_at').filter(created_by=current_user(request).customer())
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/all-offers/?'
        return render(request, 'theme/all-offers.html', {'items': items, 'paginator' : paginator, 'base_url': base_url, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class OfferDetail(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Offers.objects.get(id=item_id)
        return render(request, 'theme/offer-details.html', {'item': item, **more})


class OfferListing(View):

    def get(self, request, more={}):
        trade_type = request.GET.get('trade_type', '')
        what_crypto = request.GET.get('what_crypto', '')
        trade_price = request.GET.get('trade_price') if request.GET.get('trade_price') else 0
        flat = request.GET.get('flat', '')
        payment_method = request.GET.get('payment_method', '')
        
        if int(trade_price) > 0:
            items = models.Offers.objects.filter(Q(admin_confirmed=True, supported_location__icontains=get_set_country(request), trade_type__contains=trade_type, what_crypto__contains=what_crypto, flat__contains=flat, 
                minimum_transaction_limit__lte=trade_price, maximum_transaction_limit__gte=trade_price),
                # Q(Q(identified_user_required=get_permission_value(request, 'identified_user_required')) | Q(identified_user_required=False)),
                # Q(Q(sms_verification_required=get_permission_value(request, 'sms_verification_required')) | Q(sms_verification_required=False)),
                # Q(minimum_successful_trades__lte=get_permission_value(request, 'minimum_successful_trades')),
                # Q(minimum_complete_trade_rate__lte=get_permission_value(request, 'minimum_complete_trade_rate'))
                ).order_by('-created_at')
        else:
            items = models.Offers.objects.filter(Q(admin_confirmed=True, supported_location__icontains=get_set_country(request), 
                trade_type__contains=trade_type, what_crypto__contains=what_crypto, flat__contains=flat),
                # Q(Q(identified_user_required=get_permission_value(request, 'identified_user_required')) | Q(identified_user_required=False)),
                # Q(Q(sms_verification_required=get_permission_value(request, 'sms_verification_required')) | Q(sms_verification_required=False)),
                # Q(minimum_successful_trades__lte=get_permission_value(request, 'minimum_successful_trades')),
                # Q(minimum_complete_trade_rate__lte=get_permission_value(request, 'minimum_complete_trade_rate'))
                ).order_by('-created_at')

        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/offer-listing/?'
        return render(request, 'theme/offer-listing.html', {'items': items, 'paginator' : paginator, 'base_url': base_url,
            'trade_type': trade_type, 'what_crypto': what_crypto, 'trade_price': trade_price, 'flat': flat, 'payment_method': payment_method, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class BuyListing(View):

    def get(self, request, more={}):
        return render(request, 'theme/index.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class SellListing(View):

    def get(self, request, more={}):
        return render(request, 'theme/index.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class SingleOfferDetail(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Offers.objects.get(id=item_id)
        return render(request, 'theme/single-offer-details.html', {'item': item, **more})
    
    def post(self, request):
        item_id = request.POST.get('item_id', '')
        offer = models.Offers.objects.get(id=item_id)
        try:
            list = models.Lists.objects.get(offer=offer, created_by=current_user(request).customer())
            return self.get(request, {'item_id': item_id, 'alert': {'warning': 'Already listed.'}})
        except:
            list = models.Lists(
                offer=offer,
                created_by=current_user(request).customer()
            )
            list.save()
            return self.get(request, {'item_id': item_id, 'alert': {'success': 'Added to your list.'}})


def generate_trade_id():
    return random.choice(string.ascii_letters).upper() + str(random.randrange(9)) + str(round(datetime.now().timestamp()))


@method_decorator(customer_user_login_required, name='dispatch')
class InitiateTrade(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        trade_id = more['trade_id'] if 'trade_id' in more else request.GET.get('trade_id', '')
        return render(request, 'theme/initiate-trade.html', {'offer_id': item_id, 'trade_id': trade_id, **more})

    def post(self, request):
        offer_id = request.POST.get('offer_id', '')
        trade_id = request.POST.get('trade_id', '')
        if trade_id:
            trade = models.Trades.objects.get(id=trade_id)
        else:
            offer = models.Offers.objects.get(id=offer_id)
            try:
                trade = models.Trades()
                trade.id = generate_trade_id()
                trade.vendor = current_user(request).customer()
                trade.offer = offer
                trade.status='waiting'
                trade.save()
            except Exception as e:
                pass

        payment_method = request.POST.get('payment_method', '')
        amount = request.POST.get('amount', '')
        try:
            trade.payment_method = payment_method
            trade.amount = amount
            trade.status = 'waiting'
            trade.trade_initiator = current_user(request).customer()
            trade.trade_date = datetime.now()
            trade.save()

            escrow1, craeted1 = models.Escrows.objects.get_or_create(trade=trade, held_from=trade.seller(), held_for=trade.buyer(), defaults={
                'created_at': datetime.now(), 'status': False, 'amount': amount, 'currency': trade.offer.what_crypto
            })
            escrow1.amount = amount
            escrow1.currency = trade.offer.what_crypto
            escrow1.save()

            # escrow2, craeted2 = models.Escrows.objects.get_or_create(trade=trade, held_for=trade.seller(), held_from=trade.buyer(), defaults={
            #     'created_at': datetime.now(), 'status': False, 'amount': trade.flat_amount(), 'currency': trade.trade_flat()
            # })
            # escrow2.amount = trade.flat_amount()
            # escrow2.currency = trade.trade_flat()
            # escrow2.save()

            userrel1, created3 = models.UserRelations.objects.get_or_create(user=trade.buyer().user, partner=trade.seller().user, defaults={'created_at': datetime.now()})
            # userrel2, created4 = models.UserRelations.objects.get_or_create(user=trade.seller().user, partner=trade.buyer().user, defaults={'created_at': datetime.now()})

            # calculate_escrow(escrow.pk)#[[[?]]]
            return redirect(app_url+'/trade-processed?item_id='+str(trade.pk))
        except Exception as e:
            print(e)
            return self.get(request, {'item_id': offer_id, 'alert': {'warning': 'Sorry, Try again.'}})


def caculateTrade(request):
    offer_id = request.POST.get('offer_id', '')
    trade_id = request.POST.get('trade_id', '')
    if trade_id:
        trade = models.Trades.objects.get(id=trade_id)
        price = trade.price
        flat = trade.flat
        crypto = trade.offer.what_crypto
        mode = trade.offer.trade_type
    else:
        offer = models.Offers.objects.get(id=offer_id)
        price = offer.trade_price
        flat = offer.flat
        crypto = offer.what_crypto
        mode = offer.trade_type
        
    payment_method = request.POST.get('payment_method', '')
    amount = float(request.POST.get('amount'))
    if mode == 'buy':
        you_pay_amount = "{:.4f}".format(amount)
        you_pay_flat = crypto
        you_get_amount = "{:.1f}".format(amount*price * 0.95)
        you_get_flat = flat

        offerer_pay_amount = "{:.1f}".format(amount*price)
        offerer_pay_flat = flat
        you_cover_amount = "{:.1f}".format(amount*price * 0.95)
        you_cover_flat = flat
    else:
        you_get_amount = "{:.4f}".format(amount * 0.95)
        you_get_flat = crypto
        you_pay_amount = "{:.1f}".format(amount * price)
        you_pay_flat = flat

        offerer_pay_amount = "{:.4f}".format(amount)
        offerer_pay_flat = crypto
        you_cover_amount = "{:.4f}".format(amount * 0.95)
        you_cover_flat = crypto

    return JsonResponse({
        'you_pay_amount': you_get_amount, 'you_pay_flat': you_get_flat,
        'you_get_amount': you_pay_amount, 'you_get_flat': you_pay_flat,
        'offerer_pay_amount': offerer_pay_amount, 'offerer_pay_flat': offerer_pay_flat,
        'you_cover_amount': you_cover_amount, 'you_cover_flat': you_cover_flat
    })


@method_decorator(customer_user_login_required, name='dispatch')
class TradeProcessed(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Trades.objects.get(id=item_id)
        return render(request, 'theme/trade-processed.html', {'item': item, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class ProofOfTransaction(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Trades.objects.get(id=item_id)
        return render(request, 'theme/proof-of-transaction.html', {'item': item, **more})

    def post(self, request):
        trade_id = request.POST.get('trade_id', '')
        trade = models.Trades.objects.get(id=trade_id)
        proof_gift_code = request.POST.get('proof_gift_code', '')
        reference_number = request.POST.get('reference_number', '')
        proof_documents = request.POST.get('proof_documents', '')
        # proof_not_opened = request.POST.get('proof_not_opened', '')
        try:
            trade.proof_gift_code = proof_gift_code
            trade.proof_documents = proof_documents
            trade.reference_number = reference_number
            trade.status = 'archived'
            trade.save()
            return self.get(request, {'item_id': trade_id, 'success': True})
        except Exception as e:
            print(e)
            return self.get(request, {'item_id': trade_id, 'alert': {'warning': 'Sorry, Try again.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class TradeComplete(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Trades.objects.get(id=item_id)
        return render(request, 'theme/trade-complete.html', {'item': item, **more})

    def post(self, request):
        trade_id = request.POST.get('trade_id', '')
        trade = models.Trades.objects.get(id=trade_id)
        review_rate = request.POST.get('rate', '')
        try:
            try: 
                review = models.Reviews.objects.get(created_by=current_user(request).customer(), trade=trade)
            except:
                review = models.Reviews()
                review.trade = trade
                review.created_by = current_user(request).customer()

            review.to_customer = trade.buyer() if trade.seller() == current_user(request).customer() else trade.seller()
            review.as_role = 'buyer' if trade.seller() == current_user(request).customer() else 'seller'
            review.review_rate = review_rate
            review.created_at = datetime.now()
            review.save()
            return self.get(request, {'item_id': trade_id, 'alert': {'success': 'Rate submited.'}})
        except Exception as e:
            print(e)
            return self.get(request, {'item_id': trade_id, 'alert': {'warning': 'Sorry, Try again.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class SendCounterOffer(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        return render(request, 'theme/send-offer.html', {'offer_id': item_id, **more})

    def post(self, request):
        offer_id = request.POST.get('offer_id', '')
        offer = models.Offers.objects.get(id=offer_id)
        try:
            try:
                counter = models.Trades.objects.get(offer=offer, vendor=current_user(request).customer())
            except:
                counter = models.Trades()
                counter.id = generate_trade_id()
                counter.offer = offer
                counter.vendor = current_user(request).customer()
            counter.price = request.POST.get('price')
            counter.flat = request.POST.get('flat', '')
            counter.message = request.POST.get('message', '').strip()
            counter.created_at = datetime.now()
            counter.status = 'waiting'
            counter.save()

            message = models.Messages()
            message.message_type = 'message'
            message.content = counter.message
            message.partner = counter.offer.created_by.user
            message.writer = current_user(request)
            message.created_at = datetime.now()
            message.save()

            return self.get(request, {'item_id': offer_id, 'alert': {'success': 'Sent your offer.'}})
        except Exception as e:
            print(e)
            return self.get(request, {'item_id': offer_id, 'alert': {'warning': 'Sorry, Try again.'}})



@method_decorator(customer_user_login_required, name='dispatch')
class WatchList(View):

    def get(self, request, more={}):
        user = current_user(request)
        items = models.Lists.objects.filter(created_by=current_user(request).customer()).order_by('-created_at')
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/watch-list/?'
        return render(request, 'theme/watch-list.html', {'items': items, 'paginator' : paginator, 'base_url': base_url, **more})
    
    def post(self, request):
        item_id = request.POST.get('item_id', '')
        item = models.Lists.objects.get(id=item_id)
        try:
            item.delete()
            return JsonResponse({'success': 'Successfuly removed.'})
        except:
            return JsonResponse({'error': 'ERROR! Try later.'})


@method_decorator(customer_user_login_required, name='dispatch')
class FlagFeedback(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Reviews.objects.get(id=item_id)
        return render(request, 'theme/flag-feedback.html', {'item': item, **more})
    
    def post(self, request):
        review_id = request.POST.get('review_id', '')
        review = models.Reviews.objects.get(id=review_id)
        reason = request.POST.get('reason', '')
        content = request.POST.get('content', '')
        try:
            flag_feedback = models.FlaggedFeedback()
            flag_feedback.review = review
            flag_feedback.reason = reason
            flag_feedback.content = content
            flag_feedback.created_by = current_user(request)
            flag_feedback.created_at = datetime.now()
            flag_feedback.save()
            return self.get(request, {'item_id': review_id, 'alert' : {'success': 'Successfuly saved.'}})
        except Exception as e:
            print(e)
            return self.get(request, {'item_id': review_id, 'alert' : {'warning': 'Not saved. Try later.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class LeaveReview(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Reviews.objects.get(id=item_id)
        return render(request, 'theme/leave-review.html', {'item': item, **more})
    
    def post(self, request):
        item_id = request.POST.get('item_id', '')
        item = models.Reviews.objects.get(id=item_id)
        feedback = request.POST.get('feedback', '')
        try:
            item.feedback = feedback
            item.save()
            return redirect(app_url+'/trade-complete?item_id='+str(item.trade.id))
        except:
            return self.get(request, {'item_id': item_id, 'alert' : {'warning': 'Not saved. Try later.'}})

@method_decorator(customer_user_login_required, name='dispatch')
class IndependentEscrow(View):

    def get(self, request, more={}):
        confirmed = request.GET.get('confirmed') if request.GET.get('confirmed') else 'opened'
        status = request.GET.get('status') if request.GET.get('status') else 'all'
        trade_id = request.GET.get('trade_id')
        trade = models.Trades.objects.get(id=trade_id)
        if status == 'all':
            items = models.Escrows.objects.filter(trade=trade, confirmed=confirmed)
        elif status == 'not_funded':
            items = models.Escrows.objects.filter(trade=trade, confirmed=confirmed, status=False)
        elif status == 'funded':
            items = models.Escrows.objects.filter(trade=trade, confirmed=confirmed, status=True)
        return render(request, 'theme/independent-escrow.html', {'items': items, 'trade_id': trade_id, 'status': status, 'confirmed': confirmed, **more})

    def post(self, request):
        escrow_id = request.POST.get('item_id')
        try:
            escrow = models.Escrows.objects.get(id=escrow_id)
            currency = escrow.currency
            crypto_amount = escrow.amount

            if currency == "BTC":
                btc_processor = BTCProcessor(current_user(request).customer())
                target_addr = btc_processor.get_target_wallet_addr(customer=escrow.held_for)
                res = btc_processor.send_tx(target_addr, crypto_amount)

            if currency == "ETH":
                eth_processor = ETHProcessor(current_user(request).customer())
                target_addr = eth_processor.get_target_wallet_addr(customer=escrow.held_for)
                res = eth_processor.send_tx(target_addr, crypto_amount)

            if currency == "XRP":
                xrp_processor = XRPProcessor(current_user(request).customer())
                target_addr = xrp_processor.get_target_wallet_addr(customer=escrow.held_for)
                res = xrp_processor.send_tx(target_addr, crypto_amount)
            
            if res:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'failed': True})
        except Exception as e:
            return JsonResponse({'failed': True})



@method_decorator(customer_user_login_required, name='dispatch')
class VendorProofOfTransaction(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Trades.objects.get(id=item_id)
        if item.is_gift_card():
            return redirect(app_url+'/vpof-gift-card-steps?item_id='+item_id)

        return render(request, 'theme/vendor-proof-of-transaction.html', {'item': item, **more})

    def post(self, request):
        item_id = request.POST.get('item_id', '')
        try:
            trade = models.Trades.objects.get(id=item_id)
            # escrow = models.Escrows.objects.get(trade=trade, held_from=current_user(request).customer())
            # target_addr = escrow.held_for.btc_wallet().addr

            # currency = escrow.currency

            # if currency == "BTC":
            #     btc_processor = BTCProcessor(current_user(request).customer())
            #     res = btc_processor.send_tx(target_addr, escrow.amount)
            #     transaction = res.tx_id
            # if currency == "ETH":
            #     eth_processor = ETHProcessor(current_user(request).customer())
            #     res = eth_processor.send_tx(target_addr, escrow.amount)
            #     transaction = res.tx_id
            # if currency == "XRP":
            #     xrp_processor = XRPProcessor(current_user(request).customer())
            #     res = xrp_processor.send_tx(target_addr, escrow.amount)
            #     transaction = res.tx_id

            # if currency == "USD":
            #     paypal = None
            #     transaction = None

            # escrow.transaction = transaction
            # escrow.status = True
            # escrow.confirmed = 'closed'
            # escrow.save()

            
            if trade.vendor == current_user(request).customer():
                trade.vendor_confirm = True
            if trade.offer.created_by == current_user(request).customer():
                trade.offerer_confirm = True
            if trade.vendor_confirm and trade.offerer_confirm:
                trade.status = 'completed'
            trade.trade_date = datetime.now()
            trade.save()
            return self.get(request, {'item_id': item_id, 'alert' : {'success': 'Trade Approved.'}})
        except Exception as e:
            print(e)
            return self.get(request, {'item_id': item_id, 'alert' : {'warning': e}})



@method_decorator(customer_user_login_required, name='dispatch')
class VPOFGiftCardSteps(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        return render(request, 'theme/vpof-giftcard-steps.html', {'item_id': item_id, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class VPOFGiftCardOpenCode(View):

    def get(self, request, more={}):
        item_id = more['item_id'] if 'item_id' in more else request.GET.get('item_id', '')
        item = models.Trades.objects.get(id=item_id)
        return render(request, 'theme/vpof-giftcard-open-code.html', {'item':item, **more})

    def post(self, request, more={}):
        item_id = request.POST.get('item_id', '')
        try:
            item = models.Trades.objects.get(id=item_id)
            item.status = 'completed'
            item.proof_opened = True
            item.trade_date = datetime.now()
            item.save()
            return JsonResponse({'success': 'Gift Card Opend.', 'proof_gift_code': item.proof_gift_code})
        except:
            return JsonResponse({'error': 'Sorry, Something Wrong. Try later.'})


@method_decorator(customer_user_login_required, name='dispatch')
class Send(View):

    def get(self, request, more={}):
        return render(request, 'theme/send.html', {**more})

    def post(self, request):
        try:
            item = models.SendCryptos()
            item.crypto_amount = float(request.POST.get('crypto_amount'))
            item.flat_amount = float(request.POST.get('flat_amount'))
            item.receiver_email = request.POST.get('receiver_email')
            item.currency = request.POST.get('currency')
            item.description = request.POST.get('description')
            item.created_by = current_user(request).customer()

            if item.currency == "BTC":
                btc_processor = BTCProcessor(current_user(request).customer())
                target_addr = btc_processor.get_target_wallet_addr(None, item.receiver_email)
                res = btc_processor.send_tx(target_addr, item.crypto_amount)

            if item.currency == "ETH":
                eth_processor = ETHProcessor(current_user(request).customer())
                target_addr = eth_processor.get_target_wallet_addr(None, item.receiver_email)
                res = eth_processor.send_tx(target_addr, item.crypto_amount)

            if item.currency == "XRP":
                xrp_processor = XRPProcessor(current_user(request).customer())
                target_addr = xrp_processor.get_target_wallet_addr(None, item.receiver_email)
                res = xrp_processor.send_tx(target_addr, item.crypto_amount)

            item.receiver_attr = target_addr
            item.transaction_hash = res
            item.save()
            return self.get(request, {'success': 'Sent.'})
        except Exception as e:
            print(e)
            return self.get(request, {'warning': 'Error!. Try later.'})


@method_decorator(customer_user_login_required, name='dispatch')
class Receive(View):

    def get(self, request, more={}):
        mode = request.GET.get('mode', 'BTC')
        if mode == 'BTC':
            items = []
        if mode == 'ETH':
            items = []
        if mode == 'XRP':
            items = []
        return render(request, 'theme/receive.html', {'mode':mode, 'items': items, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class TradeHistory(View):

    def get(self, request, more={}):
        mode = request.GET.get('mode', 'sold')
        if mode == 'sold':
            items = models.Trades.objects.filter(Q(status__in=['completed', 'cancelled']), Q(Q(offer__created_by=current_user(request).customer(), offer__trade_type='sell') | Q(vendor=current_user(request).customer(), offer__trade_type='buy')))
        if mode == 'bought':
            items = models.Trades.objects.filter(Q(status__in=['completed', 'cancelled']), Q(Q(offer__created_by=current_user(request).customer(), offer__trade_type='buy') | Q(vendor=current_user(request).customer(), offer__trade_type='sell')))
        if mode == 'successful':
            items = models.Trades.objects.filter(Q(status='completed'), Q(Q(offer__created_by=current_user(request).customer()) | Q(vendor=current_user(request).customer())))
        if mode == 'cancelled':
            items = models.Trades.objects.filter(Q(status='cancelled'), Q(Q(offer__created_by=current_user(request).customer()) | Q(vendor=current_user(request).customer())))

        return render(request, 'theme/trade-history.html', {'mode':mode, 'items': items, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class SavedWallet(View):

    def get(self, request, more={}):
        return render(request, 'theme/saved-wallet.html', {**more})

    def post(self, request):
        item_id = request.POST.get('item_id', '')
        status = request.POST.get('status', '')
        crypto = request.POST.get('crypto', '')
        try:
            if crypto == "BTC":
                savedwallet = crypto.models.BTC.objects.get(id=item_id)
            if crypto == "ETH":
                savedwallet = crypto.models.ETH.objects.get(id=item_id)
            if crypto == "XRP":
                savedwallet = crypto.models.XRP.objects.get(id=item_id)

            savedwallet.status = status
            savedwallet.save()

            return JsonResponse({'success': 'Success.'})
        except:
            return JsonResponse({'error': 'Try again.'})


from crypto.btc import BTCProcessor
from crypto.eth import ETHProcessor
from crypto.xrp import XRPProcessor

@method_decorator(customer_user_login_required, name='dispatch')
class MyBalance(View):

    def get(self, request, more={}):
        btc_processor = BTCProcessor(current_user(request).customer()).get_balance()
        eth_processor = ETHProcessor(current_user(request).customer()).get_balance()
        xrp_processor = XRPProcessor(current_user(request).customer()).get_balance()

        return render(request, 'theme/my-balance.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class WithdrawFunds(View):

    def get(self, request, more={}):
        currency = request.GET.get('currency', '')
        return render(request, 'theme/withdraw-funds.html', {'currency': currency, **more})

    def post(self, request):
        currency = request.POST.get('currency', '')
        amount = request.POST.get('amount', '')
        details = request.POST.get('details', '')
        # [[[?]]]put money to card.
        try:
            obj, created = models.Balance.objects.get_or_create(customer=current_user(request).customer(), currency=currency)
            obj.amount = obj.amount - float(amount)
            if obj.amount < 0:
                return self.get(request, {'alert': {'warning': 'Not Enough your balance for '+currency}})
            obj.save()
            drawlist = models.DrawLists()
            drawlist.draw_type = 'withdraw'
            drawlist.amount = float(amount)
            drawlist.currency = currency
            drawlist.details = details
            drawlist.created_by = current_user(request).customer()
            drawlist.save()
            return self.get(request, {'alert': {'success': amount+' '+currency+' Withdrawed.'}})
        except Exception as e:
            print(e)
            return self.get(request, {'alert': {'warning': 'Try again.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class Deposits(View):

    def get(self, request, more={}):
        return render(request, 'theme/deposits.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class Withdrawals(View):

    def get(self, request, more={}):
        return render(request, 'theme/withdrawals.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class Messages(View):
    
    def get(self, request):
        client_id = request.GET.get('for')
        try:
            partner = models.Users.objects.get(id=client_id)
            relation = models.UserRelations.objects.get(user=current_user(request), partner=partner)
        except:
            partner = None
            relation = None
        return render(request, 'theme/messages.html', {'partner': partner, 'relation': relation})

    def post(self, request):
        page = request.POST.get('page')
        relation_id = request.POST.get('relation_id')
        relation = models.UserRelations.objects.get(id=relation_id)
        message_html = render_to_string('theme/message-container.html', { 'relation': relation, 'user': current_user(request) })
        return HttpResponse(message_html)



@method_decorator(customer_user_login_required, name='dispatch')
class InvitationInMessage(View):

    def get(self, request, more={}):
        return render(request, 'theme/invitation-in-message.html', {**more})


@method_decorator(customer_user_login_required, name='dispatch')
class IdVerification(View):

    def get(self, request, more={}):
        items = current_user(request).id_cards_list()
        return render(request, 'theme/id-verification.html', { 'items': items, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class Notifications(View):

    def get(self, request, more={}):
        notifications = []
        processed_trades = models.Trades.objects.filter(Q(Q(offer__created_by=current_user(request).customer()) | Q(vendor=current_user(request).customer()), Q(status__in=['waiting', 'archived', 'completed'])) | Q(status='accepted', vendor=current_user(request).customer()))
        for trade in processed_trades:
            trade_id = str(trade.id)
            if trade.status == 'accepted':
                notifications.append({'text': 'Your offer. '+trade_id+' has been accepted by offerer. <b>Start</b> your trade.', 'url': app_url+'/initiate-trade?item_id='+trade_id})
            if trade.status == 'waiting':
                notifications.append({'text': 'Trade No. '+trade_id+' has been processed. <b>Archive</b> your proof of transaction.', 'url': app_url+'/trade-processed?item_id='+trade_id})
            if trade.status == 'archived':
                notifications.append({'text': '<b>Review</b> proof of transaction for Trade No. '+trade_id+'.', 'url': app_url+'/vendor-proof-of-transaction?item_id='+trade_id})
            if trade.status == 'completed' and not trade.reviewed_by(current_user(request).customer()):
                notifications.append({'text': 'Trade No. '+trade_id+' completed. <b>Remain</b> your feedback.', 'url': app_url+'/trade-complete?item_id='+trade_id})

        return render(request, 'theme/notifications.html', {'items': notifications, **more})


class BlogListing(View):

    def get(self, request, more={}):
        items = models.Posts.objects.filter(status='Publish')
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number, 9)
        base_url = app_url+'/blog-listing/?'

        return render(request, 'theme/blog-listing.html', {'items': items, 'paginator' : paginator, 'base_url': base_url, **more})


class BlogDetail(View):

    def get(self, request, more={}):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Posts.objects.get(id=item_id)
        return render(request, 'theme/blog-detail.html', {'item': item, **more})


@method_decorator(customer_user_login_required, name='dispatch')
class Vendors(View):

    def get(self, request, more={}):
        q = request.GET.get('q', '').strip()
        s = request.GET.get('s', 'active').strip()
        status = True
        if s == 'active':
            status = True
        elif s == 'new':
            status = False

        items = models.Customers.objects.filter(user__username__contains=q, customer_type='sell', user__is_customer=status)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/vendors/?'
        return render(request, 'theme/seller-directory.html', {'items': items, 's': s, 'q':q, 'paginator' : paginator, 'base_url': base_url, **more})

    def post(self, request):
        q = request.POST.get('q', '').strip()
        s = request.POST.get('s', 'active').strip()
        status = True
        if s == 'active':
            status = True
        elif s == 'new':
            status = False
        items = list(models.Customers.objects.filter(user__username__contains=q, customer_type='sell', user__is_customer=status).values_list('user__username', flat=True)[:10])
        return JsonResponse({'items': items})


class Contact(View):

    def get(self, request, more={}):
        return render(request, 'theme/contact.html', {**more})

    def post(self, request):
        fullname = request.POST.get('fullname', '')
        email_address = request.POST.get('email_address', '')
        use_my_email = request.POST.get('use_my_email', '')
        subject = request.POST.get('subject', '').strip()
        content = request.POST.get('content', '').strip()
        user = None
        if use_my_email == 'on':
            try:
                # user = models.Users.objects.get(token=request.session['user'])
                user = request.user
                email_address = user.email
            except:
                return self.get(request, {'error': {'email_address': 'Not valid email address.'}})
        elif email_address == '':
            return self.get(request, {'error': {'email_address': 'Email address is required.'}})

        contact = models.Contacts()
        contact.fullname = fullname
        contact.email_address = email_address
        contact.subject = subject
        contact.content = content
        contact.user = user
        contact.ip_address = get_client_ip(request)
        contact.save()

        return self.get(request, {'alert': {'success': 'Message is sent successfuly. We will contact you soon.'}})


@method_decorator(customer_user_login_required, name='dispatch')
class Referrals(View):

    def get(self, request, more={}):
        return render(request, 'theme/referrals.html', {**more})

    def post(self, request):
        email = request.POST.get('email', '')
        fullname = request.POST.get('fullname', '')
        message = request.POST.get('message', '').strip()
        if current_user(request).send_invite_email(email, fullname, message):
            return self.get(request, {'alert': {'success': 'Invite Email Sent.'}})
        else:
            return self.get(request, {'alert': {'warning': 'Sorry!. Try Later!'}})


class Buy(View):
    
    def get(self, request):
        template_name = 'theme/buy-listing.html'
        if request.LANGUAGE_CODE == 'zh-hans':
            template_name = 'theme/landing-china-all-coins.html'
        items = models.Trades.objects.filter(status=True).order_by('-created_at')[:5]
        return render(request, template_name, {'items': items})


@method_decorator(customer_user_login_required, name='dispatch')
class AddMessage(View):
    
    def post(self, request):
        message_type = request.POST.get('message_type', '')
        if message_type == 'ticket':
            ticket_id = request.POST.get('ticket_id', '')
            ticket = models.Tickets.objects.get(id=ticket_id)
            content = request.POST.get('content', '')
            writer = current_user(request)

            try:
                message = models.Messages()
                message.message_type = message_type
                message.ticket = ticket
                message.content = content
                message.writer = writer
                message.created_at = datetime.now()
                message.save()
                return TicketDetails.get(TicketDetails, request, {'item_id': ticket_id, 'alert': {'success': 'Added.'}})
            except Exception as e:
                print(e)
                return TicketDetails.get(TicketDetails, request, {'item_id': ticket_id, 'alert': {'warning': 'ERROR! Try again.'}})

        if message_type == 'message':
            partner_id = request.POST.get('partner_id', '')
            partner = models.Users.objects.get(id=partner_id)
            content = request.POST.get('content', '')
            writer = current_user(request)

            try:
                message = models.Messages()
                message.message_type = message_type
                message.partner = partner
                message.content = content
                message.writer = writer
                message.created_at = datetime.now()
                message.save()
                return JsonResponse({'success': True})
            except Exception as e:
                print(e)
                return JsonResponse({'success': False})
        


def do_paginate(data_list, page_number, per_page=10):
    ret_data_list = data_list
    result_per_page = per_page
    paginator = Paginator(data_list, result_per_page)
    try:
        ret_data_list = paginator.page(page_number)
    except EmptyPage:
        ret_data_list = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        ret_data_list = paginator.page(1)
    return ret_data_list, paginator


from cadmin.form import MediasForm

@method_decorator(customer_user_login_required, name='dispatch')
class UploadView(View):

    def post(self, request):
        mode = request.POST.get('mode')
            
        form = MediasForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            media = form.save()
            media.created_by = current_user(request)
            media.save()
            if mode == 'id_card':   
                card_id = request.POST.get('card_id')
                userids = models.UserIDs.objects.get(id=card_id)
                userids.images = ",".join([str(im.id) for im in userids.images_list()]+[str(media.id)])
                userids.save()

            data = {'is_valid': True, 'name': media.file.name, 'url': media.file.url, 'id': media.pk}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def calculate_escrow(escrow_id):
    return True


from loremipsum import get_sentence
def makeing_fake_trade(request):
    crypto = ['BTC', 'ETH', 'XRP'][random.randrange(3)]
    flat_index = random.randrange(4)
    flats = ['USD', 'EUR', 'GBP', 'JPY']
    flat = flats[flat_index]
    country = ['GB', 'US', 'RU', 'JP', 'CN'][random.randrange(5)]
    cities = {
        'GB': ['London', 'Manchester', 'Liverpool', 'Bristol', 'Oxford'],
        'US': ['New York', 'Washinton', 'Chicago', 'San Francisco', 'Los Angeles'],
        'RU': ['Ruxenburg', 'Moscrow', 'Sibiri', 'Samara', 'Omsk'],
        'JP': ['Tokyo', 'Hirosima', 'Nagasakki', 'Yokohama', 'Sapporo'],
        'CN': ['Beijing', 'Wuhan', 'HongKong', 'Taiwan', 'ShangHai']
    }
    city = cities[country][random.randrange(5)]
    rate = CurrencyExchangeData().get_price(crypto, 'USD')
    trade_price = rate + rate*(random.randrange(200)-100)/10000
    times = 400 if crypto == "ETH" else 40000 if crypto == "XRP" else 1
    supported_location = []
    for i in range(random.randrange(5)):
        supported_location.append(['GB', 'US', 'RU', 'JP', 'CN'][random.randrange(5)])
    supported_location = [country] if supported_location == [] else supported_location
    created_at = datetime.now() - timedelta(days=random.randrange(90))
    customers = models.Customers.objects.all()
    customers_array = [k for k in range(customers.count())]
    cus_index = random.randrange(len(customers_array))
    created_by = customers[cus_index]

    offer_data = {
        'trade_type': ['buy', 'sell'][random.randrange(2)],
        'what_crypto': crypto,
        'flat': flat,
        'postal_code': random.randrange(10000, 99999),
        'show_postcode': [True, False][random.randrange(2)],
        'country': country,
        'city': city,
        'trade_price': trade_price,
        'use_market_price': [True, False][random.randrange(2)],
        'trail_market_price': False,
        'profit_start': None,
        'profit_end': None,
        'profit_time': 0,
        'minimum_transaction_limit': random.randrange(3*times),
        'maximum_transaction_limit': random.randrange(3*times, 10*times),
        'operating_hours_start': '{:%H:%M}'.format(datetime(2000, 1, 1, random.randrange(8, 15), random.randrange(60))),
        'operating_hours_end': '{:%H:%M}'.format(datetime(2000, 1, 1, random.randrange(15, 20), random.randrange(60))),
        'restrict_hours_start': '{:%H:%M}'.format(datetime(2000, 1, 1, random.randrange(12, 13), random.randrange(60))),
        'restrict_hours_end': '{:%H:%M}'.format(datetime(2000, 1, 1, random.randrange(13, 14), random.randrange(60))),
        'proof_times': random.randrange(6),
        'supported_location': supported_location,
        'trade_overview': get_sentence(random.randrange(10)),
        'message_for_proof': get_sentence(random.randrange(3)),
        'identified_user_required': [True, False][random.randrange(2)],
        'sms_verification_required': [True, False][random.randrange(2)],
        'minimum_successful_trades': [0, 0, 0, random.randrange(20)][random.randrange(4)],
        'minimum_complete_trade_rate': [0, 0, 0, random.randrange(50, 90)][random.randrange(4)],
        'admin_confirmed': True,#False
        'created_at': created_at
    }

    offer = models.Offers()
    try:
        offer.__dict__.update(offer_data)
        offer.created_by = created_by
        offer.save()
    except Exception as e:
        return JsonResponse(e)

    return_data = {}
    return_data.update({'offer': "[{}] {} => {} ({})".format(offer.created_by, offer.what_crypto if offer.trade_type == "sell" else offer.flat, 
        offer.flat if offer.trade_type == "sell" else offer.what_crypto, offer.trade_price)})

    customers_array.pop(cus_index)
    flats.pop(flat_index)

    for i in range(3):
        if [True, False, True, False, False, False, False][random.randrange(i-1, 2*i)]:
            try:
                cus_array_index = random.randrange(len(customers_array))
                cus_index = customers_array[cus_array_index]
                vendor = customers[cus_index]
                customers_array.pop(cus_array_index)
                vendor = models.Users.objects.get(username="dev_srecorder").customer() if request.GET.get('m', '') == 'screen' and created_by != 'dev_srecorder' else vendor

                trade_created_at = created_at + timedelta(days=random.randrange(30))
                trade_date = trade_created_at + timedelta(days=random.randrange(5))

                trade = models.Trades()
                trade.id = generate_trade_id()
                trade.vendor = vendor
                trade.offer = offer
                trade.payment_method = ['cash_deposit', 'bank_transfer', 'paypal', 'pingit', 'cash_in_person', 'amazon_gc', 
                    'itunes_gc', 'steam_gc', 'other'][random.randrange(9)] if request.GET.get('m', '') != 'screen' else ['amazon_gc', 'itunes_gc', 'steam_gc'][random.randrange(3)]
                trade.amount = (offer.maximum_transaction_limit - offer.minimum_transaction_limit)*random.randrange(100)/100 + offer.minimum_transaction_limit
                trade.status = ['counting', 'declined', 'waiting', 'archived', 'archived', 'completed', 'cancelled'][round(random.randrange(560)/100)] if request.GET.get('m', '') != 'screen' else 'archived'
                trade.trade_initiator = [created_by, vendor][random.randrange(2)]
                
                if trade.status in ['archived', 'completed', 'cancelled']:
                    trade.trade_date = trade_date

                if trade.status == 'completed':
                    if '_gc' in trade.payment_method:
                        trade.proof_gift_code = get_random_string(20)
                        trade.proof_opened = True
                    else:
                        trade.reference_number = random.randrange(1000000, 9999999)

                trade.flat = flats[random.randrange(3)]
                trade.price = offer.trade_price - rate*(random.randrange(100))/10000
                trade.message = get_sentence(random.randrange(5))
                
                trade.created_at = trade_created_at
                trade.save()


                escrow1 = models.Escrows()
                escrow1.trade = trade
                escrow1.held_for = trade.buyer()
                escrow1.held_from = trade.seller()
                escrow1.created_at = trade_created_at
                escrow1.amount = trade.amount
                escrow1.status = False
                escrow1.currency = trade.offer.what_crypto

                # escrow2 = models.Escrows()
                # escrow2.trade = trade
                # escrow2.held_for = trade.seller()
                # escrow2.held_from = trade.buyer()
                # escrow2.created_at = trade_created_at
                # escrow2.amount = trade.flat_amount()
                # escrow2.status = False
                # escrow2.currency = trade.trade_flat

                if trade.status == 'completed':
                    escrow1.confirmed = 'closed'
                    escrow1.status = True
                    # escrow2.confirmed = 'closed'
                    # escrow2.status = True

                    review1 = models.Reviews()
                    review1.as_role = 'buyer'
                    review1.review_rate = [3, 4, 5, 5, 5][random.randrange(5)]
                    review1.feedback = get_sentence(random.randrange(5))
                    review1.created_at = trade_created_at
                    review1.created_by = trade.seller()
                    review1.to_customer = trade.buyer()
                    review1.trade = trade
                    review1.save()

                    review2 = models.Reviews()
                    review2.as_role = 'seller'
                    review2.review_rate = [3, 4, 5, 5, 5][random.randrange(5)]
                    review2.feedback = get_sentence(random.randrange(5))
                    review2.created_at = trade_created_at
                    review2.created_by = trade.buyer()
                    review2.to_customer = trade.seller()
                    review2.trade = trade
                    review2.save()


                escrow1.save()
                # escrow2.save()

                userrel1, created3 = models.UserRelations.objects.get_or_create(user=trade.buyer().user, partner=trade.seller().user, defaults={ 'blocked_at': datetime.now() if random.randrange(10) > 2 else None, 'created_at': datetime.now()})
                userrel2, created4 = models.UserRelations.objects.get_or_create(user=trade.seller().user, partner=trade.buyer().user, defaults={ 'trusted_at': datetime.now() if random.randrange(10) > 2 else None, 'created_at': datetime.now()})
            except Exception as e:
                print(e)
                return JsonResponse(e)

            return_data.update({'trade'+str(i): "[{}] {} '{}'".format(trade.vendor, trade.payment_method, trade.amount)})
    
    return JsonResponse(return_data)


