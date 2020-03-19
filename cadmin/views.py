from django.shortcuts import render

# Create your views here.
import logging
import re
import uuid
import sys
import string
from datetime import datetime, timedelta

from django.views import View
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import Extract
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator   
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.template.defaulttags import register

from . import models
from .models import COUNTRY_CODE
from .form import MediasForm
from .decorators import admin_login_required, user_not_logged_in
from django.contrib.auth import (login as auth_login, logout as auth_logout)

logger = logging.getLogger('raplev')
logger.setLevel(logging.INFO)
app_url = '/cadmin'

@register.filter
def keyvalue(dict, key):    
    try:
        return dict[str(key)]
    except:
        return ''


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def super_admin_view(request):
    if request.user.is_authenticated:
        return redirect('/cadmin')
    else:
        return redirect('/super-admin/login')


def current_user(request):
    try:
        # user = models.Users.objects.get(token=request.session['user'])
        # return user
        return request.user
    except:
        None


class Pages(View):
    
    def get(self, request, more={}):
        return render(request, 'cadmin/pages.html', {**more})


@method_decorator(user_not_logged_in, name='dispatch')
class LoginView(View):

    def get(self, request):
        return render(request, 'cadmin/login.html')

    def post(self, request):
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user = models.Users.objects.get(Q(username=email_or_username) | Q(email=email_or_username))
            if user and check_password(password, user.password) and user.is_admin:
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
                return render(request, 'cadmin/login.html', {'error': 'Incorrect Password'})
        except Exception as e:
            print(e)
            return render(request, 'cadmin/login.html', {'error': 'Incorrect User'})
        
        return redirect(app_url+'')


@admin_login_required
def logout(request):
    # del request.session['user']
    auth_logout(request)
    # request.session['global_alert'] = {'success': "You are logged out."}
    return redirect(app_url+'')


@method_decorator(admin_login_required, name='dispatch')
class IndexView(View):
    
    def get(self, request):
        return redirect(app_url+'/revenue')


@method_decorator(admin_login_required, name='dispatch')
class AddUserView(View):

    def get(self, request):
        if current_user(request).is_superuser:
            return render(request, 'cadmin/add-user.html')
        else:
            return redirect(app_url)

    def post(self, request):
        data=request.POST
        if 'update' in data and data['update'] == 'on':
            temp_user = models.Users.objects.get(email=data['email'])
            temp_user.is_admin = True
            temp_user.fullname=data['fullname']
            temp_user.username=data['username']
            temp_user.password=make_password(data['password'])
            admin = models.Admins(
                user = temp_user,
                role=data['role']
            )
        else:
            temp_user = models.Users(
                fullname=data['fullname'],
                username=data['username'],
                email=data['email'],
                password=make_password(data['password']),
                is_admin=True
            )
            admin = models.Admins(
                user=temp_user,
                role=data['role']
            )
        try:
            temp_user.save()
            admin.save()
        except Exception as err:
            if 'duplicate key value' in str(err):
                logger.info("User {} hasn't been added because of duplication.".format(temp_user.email))
                return render(request, 'cadmin/add-user.html', {'error': temp_user.email + " is already exist.", 'update': True})
            return render(request, 'cadmin/add-user.html', {'error': "Something wrong. Please try again later."})
        logger.info("User {} has been added".format(temp_user.username))
        if 'send_email' in data:
            logger.info("Send user detail email to {}".format(temp_user.username))
            temp_user.send_info_email()
        return render(request, 'cadmin/add-user.html', {'success': "User {} has been added".format(temp_user.username)})


@method_decorator(admin_login_required, name='dispatch')
class UsersView(View):

    def get(self, request):
        username = request.GET.get('username', '').strip()
        user_list = models.Admins.objects.filter(user__username__icontains=username, user__is_admin=True)
        page_number = request.GET.get('page', 1)
        user_list, paginator = do_paginate(user_list, page_number)
        base_url = app_url+'/users/?username=' + username + "&"
        return render(request, 'cadmin/users.html',
                      {'user_list': user_list, 'paginator' : paginator, 'base_url': base_url, 'search_user_name': username})


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


def get_weekdate(day):
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


@method_decorator(user_not_logged_in, name='dispatch')
class RecoverView(View):

    def get(self, request):
        return render(request, 'cadmin/recover.html')

    def post(self, request):
        email = request.POST.get('email', '').strip()

        try:
            user = models.Users.objects.get(email=email)
            if user:
                user.send_recover_email('cadmin')
                return render(request, 'cadmin/recover.html', {'success': 'Please check your email.'})
            else:
                return render(request, 'cadmin/recover.html', {'error': 'Incorrect User'})
        except Exception as e:
            print(e)
            return render(request, 'cadmin/recover.html', {'error': 'Sorry, Something wrong. Please try later.'})
        

@method_decorator(user_not_logged_in, name='dispatch')
class SetPWView(View):

    def get(self, request):
        token = request.GET.get('t', '').strip()
        try:
            user = models.Users.objects.get(token=token)
            now = datetime.utcnow().timestamp()
            expiration_time = int(token[80:], 0)/10000
            if expiration_time >= now:
                return render(request, 'cadmin/set-pw.html', {'token': token})
            else:
                return render(request, 'cadmin/error.html', {'error': 'Sorry this request is expired. Try again.'})
        except Exception as e:
            print(e)
            return render(request, 'cadmin/error.html', {'error': 'Sorry this request is NOT available. Try again.'})


    def post(self, request):
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        token = request.POST.get('token', '').strip()

        if password != password_confirm:
            return render(request, 'cadmin/set-pw.html', {'error': 'Please confirm password.'})
        try:
            user = models.Users.objects.get(token=token)
            if user:
                user.password = make_password(data['password'])
                user.save()
            else:
                return render(request, 'cadmin/set-pw.html', {'success': 'Success reset password.'})
        except:
            return render(request, 'cadmin/set-pw.html', {'error': 'Sorry, Something wrong. Please try later.'})
        
        return redirect(app_url+'')


@method_decorator(admin_login_required, name='dispatch')
class RevenueView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.Revenue.objects.filter(source__icontains=search, date__range=(start_date, end_date))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/revenue/?search=' + search + "&start_date=" + start_date + "&end_date=" + end_date + "&"
        return render(request, 'cadmin/revenue.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 
                      'start_date': start_date, 'end_date': end_date})


@method_decorator(admin_login_required, name='dispatch')
class RevenueDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Revenue.objects.get(id=item_id)
        return render(request, 'cadmin/revenue-details.html', {'item': item, })

    def post(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Revenue.objects.get(id=item_id)
        item.refund = -item.amount
        item.save()
        return render(request, 'cadmin/revenue-details.html', {'item': item, 'success': 'Refunded'})


@method_decorator(admin_login_required, name='dispatch')
class RevStatsView(View):

    def get(self, request):
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        total_sum = models.Revenue.objects.filter(date__range=(start_date, end_date)).aggregate(total_earned=Sum('amount'), 
            total_refunded=Sum('refund'))
        total_earned = total_sum['total_earned'] or 0
        total_refunded = total_sum['total_refunded'] or 0
        total_count = models.Revenue.objects.filter(date__range=(start_date, end_date)).count()
        main_count = models.Revenue.objects.filter(source='Main platform', date__range=(start_date, end_date)).count()
        percentage = round(main_count/total_count*100) if total_count > 0 else 0
        return render(request, 'cadmin/rev-stats.html',
                      {'total_earned': total_earned, 'total_refunded' : total_refunded, 'percentage': percentage, 
                      'start_date': start_date, 'end_date': end_date})


@method_decorator(admin_login_required, name='dispatch')
class OffersView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.Offers.objects.filter(id__icontains=search)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/offers/?search=' + search + "&"
        return render(request, 'cadmin/offers.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})

    # def post(self, request):
    #     item_id = request.POST.get('item_id', '').strip()
    #     item = models.Offers.objects.get(id=item_id)
    #     item.suspended = True
    #     item.save()
    #     print(item)
    #     return JsonResponse({'success': 'Suspended'})


@method_decorator(admin_login_required, name='dispatch')
class OfferDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Offers.objects.get(id=item_id)
        return render(request, 'cadmin/offer-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class TradesView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        status = request.GET.get('status', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.Trades.objects.filter(id__icontains=search, status__icontains=status, created_at__range=(start_date, end_date))
        count = {}
        count['all'] = models.Trades.objects.filter(id__icontains=search, created_at__range=(start_date, end_date)).count()
        count['waiting'] = models.Trades.objects.filter(id__icontains=search, status__icontains='waiting', created_at__range=(start_date, end_date)).count()
        count['archived'] = models.Trades.objects.filter(id__icontains=search, status__icontains='archived', created_at__range=(start_date, end_date)).count()
        count['completed'] = models.Trades.objects.filter(id__icontains=search, status__icontains='completed', created_at__range=(start_date, end_date)).count()
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/trades/?search=' + search + "&start_date=" + start_date + "&end_date=" + end_date + "&"
        return render(request, 'cadmin/trades.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 'status': status, 'count': count,
                      'start_date': start_date, 'end_date': end_date})


@method_decorator(admin_login_required, name='dispatch')
class TradeDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Trades.objects.get(id=item_id)
        return render(request, 'cadmin/trade-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class CustomersView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.Customers.objects.filter(Q(user__email__icontains=search) | Q(user__username__icontains=search))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/customers/?search=' + search + "&"
        return render(request, 'cadmin/customers.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Customers.objects.get(id=item_id)
        item.set_suspend()
        return JsonResponse({'success': 'Suspended'})


@method_decorator(admin_login_required, name='dispatch')
class CustomerDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Customers.objects.get(id=item_id)
        return render(request, 'cadmin/customer-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class CustomerSuspend(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Customers.objects.get(id=item_id)
        item.set_suspend()

        return render(request, 'cadmin/customer-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class TransactionsView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.Trades.objects.filter(id__icontains=search, status='completed')
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/transactions/?search=' + search + "&"
        return render(request, 'cadmin/transactions.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})


@method_decorator(admin_login_required, name='dispatch')
class TransactionDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Trades.objects.get(id=item_id, status='completed')
        return render(request, 'cadmin/transaction-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class EscrowsView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.Escrows.objects.filter(id__icontains=search)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/escrows/?search=' + search + "&"
        return render(request, 'cadmin/escrows.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})


@method_decorator(admin_login_required, name='dispatch')
class EscrowDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Escrows.objects.get(id=item_id)
        return render(request, 'cadmin/escrow-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class EscrowRelease(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Escrows.objects.get(id=item_id)
        item.status = True
        item.save()
        return render(request, 'cadmin/escrow-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class EscrowCancel(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Escrows.objects.get(id=item_id)
        item.status = False
        item.save()
        return render(request, 'cadmin/escrow-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class SupportCenterView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        is_dispute = request.GET.get('is_dispute', '').strip()
        items = models.Tickets.objects.filter(id__icontains=search, is_dispute__icontains=is_dispute)
        count = {}
        count['All'] = models.Tickets.objects.filter(id__icontains=search).count()
        count['Disputes'] = models.Tickets.objects.filter(id__icontains=search, is_dispute=True).count()
        count['General'] = models.Tickets.objects.filter(id__icontains=search, is_dispute=False).count()
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/support-center/?search=' + search + "&"
        return render(request, 'cadmin/support-center.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 'count': count})


@method_decorator(admin_login_required, name='dispatch')
class TicketDetailsDisputeView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Tickets.objects.get(id=item_id)
        return render(request, 'cadmin/ticket-details-dispute.html', {'item': item})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        content = request.POST.get('content', '').strip()
        # attach_file = request.POST.attach_file
        item = models.Tickets.objects.get(id=item_id)
        mes = models.Messages()
        mes.partner = item.created_by
        mes.message_type = 'ticket'
        mes.ticket = item
        mes.writer = current_user(request)
        mes.content = content
        # mes.attach_file = attach_file
        mes.created_at = datetime.now()
        mes.save()
        return render(request, 'cadmin/ticket-details-dispute.html', {'item': item})


@method_decorator(admin_login_required, name='dispatch')
class TicketDetailsNoDisputeView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Tickets.objects.get(id=item_id)
        return render(request, 'cadmin/ticket-details-no-dispute.html', {'item': item})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        content = request.POST.get('content', '').strip()
        # attach_file = request.POST.attach_file
        item = models.Tickets.objects.get(id=item_id)
        mes = models.Messages()
        mes.partner = item.created_by
        mes.message_type = 'ticket'
        mes.ticket = item
        mes.writer = current_user(request)
        mes.content = content
        # mes.attach_file = attach_file
        mes.created_at = datetime.now()
        mes.save()
        return render(request, 'cadmin/ticket-details-no-dispute.html', {'item': item})


@method_decorator(admin_login_required, name='dispatch')
class TicketPriorityChange(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Tickets.objects.get(id=item_id)
        item.ticket_priority = 'Low' if item.ticket_priority == 'High' else 'High'
        item.save()
        return JsonResponse({'success': 'Ticket priority changed.', 'content': item.ticket_priority})

@method_decorator(admin_login_required, name='dispatch')
class IdVerifyAppView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.UserIDs.objects.filter(id__icontains=search)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/id-verify-app/?search=' + search + "&"
        return render(request, 'cadmin/id-verify-app.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})


@method_decorator(admin_login_required, name='dispatch')
class IdVerifyAppDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.UserIDs.objects.get(id=item_id)
        return render(request, 'cadmin/id-verify-app-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class IdVerifyAppReject(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.UserIDs.objects.get(id=item_id)
        item.status = False
        item.save()
        return render(request, 'cadmin/id-verify-app-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class IdVerifyAppAccept(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.UserIDs.objects.get(id=item_id)
        item.status = True
        item.save()
        return render(request, 'cadmin/id-verify-app-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class ContactFormView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.Contacts.objects.filter(email_address__icontains=search)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/contact-form/?search=' + search + "&"
        return render(request, 'cadmin/contact-form.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})


@method_decorator(admin_login_required, name='dispatch')
class ContactFormDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Contacts.objects.get(id=item_id)
        item.readed = True
        item.save()
        return render(request, 'cadmin/contact-form-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class AdditionalPagesView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        search_status = request.GET.get('search_status', '').strip()
        items = models.Pages.objects.filter(title__icontains=search, status__icontains=search_status)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/additional-pages/?search=' + search + "&search_status=" + search_status + "&"
        return render(request, 'cadmin/additional-pages.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 'search_status': search_status})


@method_decorator(admin_login_required, name='dispatch')
class AdditionalPagePreviewView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Pages.objects.get(id=item_id)
        return return_custom_page(request, item)


@method_decorator(admin_login_required, name='dispatch')
class AddNewPageView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Pages()
        try:
            item = models.Pages.objects.get(id=item_id)
            title = 'Edit page'
        except:
            title = 'Add new page'
        return render(request, 'cadmin/add-new-page.html', {'item': item, 'title': title})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        action = request.POST.get('action', '').strip()
        title = request.POST.get('title', '').strip()
        context = request.POST.get('context', '').strip()
        try:
            item = models.Pages.objects.get(id=item_id)
        except:
            item = models.Pages()
            item.created_at = datetime.now()
        
        item.posted_by = current_user(request)
        item.status = action
        item.title = title
        item.context = context
        item.updated_on = datetime.now()
        item.save()
        title = 'Edit page'
        return render(request, 'cadmin/add-new-page.html', {'item': item, 'title': title})


@method_decorator(admin_login_required, name='dispatch')
class MoveToTrashPage(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Pages.objects.get(id=item_id)
        item.status = 'Trash'
        item.save()
        return JsonResponse({'success': 'Moved to trash.', 'content': 'Trashed'})


@method_decorator(admin_login_required, name='dispatch')
class BlogView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        search_status = request.GET.get('search_status', '').strip()
        items = models.Posts.objects.filter(title__icontains=search, status__icontains=search_status)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/blog/?search=' + search + "&search_status=" + search_status + "&"
        return render(request, 'cadmin/blog.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 'search_status': search_status})


@method_decorator(admin_login_required, name='dispatch')
class PostPreviewView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Posts.objects.get(id=item_id)
        return render(request, 'cadmin/custom-post.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class AddNewPostView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Posts()
        try:
            item = models.Posts.objects.get(id=item_id)
            title = 'Edit post'
        except:
            title = 'Add new post'
        return render(request, 'cadmin/add-new-post.html', {'item': item, 'title': title})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        action = request.POST.get('action', '').strip()
        title = request.POST.get('title', '').strip()
        context = request.POST.get('context', '').strip()
        disallow_comments = request.POST.get('disallow_comments', False)
        featured_images = request.POST.get('featured_images', '').strip()
        featured_images = ','.join(featured_images.split(','))
        tags = request.POST.get('tags', '').strip()
        add_tags(tags, current_user(request))
        try:
            item = models.Posts.objects.get(id=item_id)
        except:
            item = models.Posts()
            item.created_at = datetime.now()
        
        item.posted_by = current_user(request)
        item.status = action
        item.title = title
        item.context = context
        item.disallow_comments = disallow_comments
        item.featured_images = featured_images
        item.tags = tags
        item.updated_on = datetime.now()
        item.save()
        title = 'Edit post'
        return render(request, 'cadmin/add-new-post.html', {'item': item, 'title': title})


def add_tags(tags, username):
    for tag in tags.split(','):
        tag = tag.strip()
        if not models.Tags.objects.filter(name=tag).exists():
            models.Tags(name=tag, created_by=username).save()


@method_decorator(admin_login_required, name='dispatch')
class BlogMoveToTrashPage(View):

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Posts.objects.get(id=item_id)
        item.status = 'Trash'
        item.save()
        return JsonResponse({'success': 'Moved to trash.', 'content': 'Trashed'})


@method_decorator(admin_login_required, name='dispatch')
class TagsView(View):

    def get(self, request):
        alpha = request.GET.get('alpha', '').strip()
        ongoing = request.GET.get('ongoing', True)
        strings = string.ascii_uppercase
        if alpha == '~A':
            items = models.Tags.objects.filter(~Q(name__range=('a', 'zzz')) & ~Q(name__range=('A', 'ZZZ')) & Q(ongoing=ongoing))
        else:
            items = models.Tags.objects.filter(name__istartswith=alpha, ongoing=ongoing)
        return render(request, 'cadmin/tags.html', {'items': items, 'alpha': alpha, 'ongoing': ongoing, 'strings':strings})

    def post(self, request):
        mode = request.POST.get('mode', '').strip()
        item_id = request.POST.get('item_id', '').strip()
        item = models.Tags.objects.get(id=item_id)
        if mode == 'ongoing-true':
            item.ongoing = True
            item.save()
            success = 'This tag is available.'
        if mode == 'ongoing-false':
            item.ongoing = False
            item.save()
            success = 'This tag is not available.'
        if mode == 'remove':
            item.delete()
            success = 'This tag deleted.'
        return JsonResponse({'success': success})


@method_decorator(admin_login_required, name='dispatch')
class MediaLibraryView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        years = sorted(set(models.Medias.objects.annotate(year=Extract('created_at', 'year')).values_list('year', flat=True)), reverse=True)
        year = request.GET.get('year', datetime.now().strftime("%Y")).strip()
        months = sorted(set(models.Medias.objects.filter(created_at__year=year).annotate(month=Extract('created_at', 'month')).values_list('month', flat=True)), reverse=True)
        month = request.GET.get('month', datetime.now().strftime("%m")).strip()
        if int(month) not in months:
            month = str(months[0]) if len(months) > 0 else '1'
        items = models.Medias.objects.filter(id__icontains=search, created_at__year=year, created_at__month=month)
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/media-library/?search=' + search + "&year=" + year + "&month=" + month + "&"
        return render(request, 'cadmin/media-library.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 
                      'years': years, 'months': months, 'year': year, 'month': month})


@method_decorator(admin_login_required, name='dispatch')
class UploadView(View):

    def get(self, request):
        return render(request, 'cadmin/upload.html', {})

    def post(self, request):
        form = MediasForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            media = form.save()
            media.created_by = current_user(request)
            media.save()
            data = {'is_valid': True, 'name': media.file.name, 'url': media.file.url, 'id': media.pk}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


@method_decorator(admin_login_required, name='dispatch')
class LastLoginView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.LoginLogs.objects.filter(ip_address__icontains=search).order_by('-created_at')
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/last-login/?search=' + search + "&"
        return render(request, 'cadmin/last-login.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})


@method_decorator(admin_login_required, name='dispatch')
class FlaggedPostsView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        items = models.FlaggedPosts.objects.filter(Q(id__icontains=search) | Q(post__id__icontains=search))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/flagged-posts/?search=' + search + "&"
        return render(request, 'cadmin/flagged-posts.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search,})


@method_decorator(admin_login_required, name='dispatch')
class FlaggedPostDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.FlaggedPosts.objects.get(id=item_id)
        return render(request, 'cadmin/flagged-post-details.html', {'item': item, })


@method_decorator(admin_login_required, name='dispatch')
class AddLandingPageView(View):

    def get(self, request, success='', error={}):
        item_id = request.GET.get('item_id', '').strip()
        delete_id = request.GET.get('delete_id', '').strip()
        if delete_id:
            try:
                models.LandingPages.objects.get(id=delete_id).delete()
                success = 'Landing page deleted.'
            except:
                error['delete_item'] = 'That page is already using by other link, please check and try again.' 
        try:
            item = models.LandingPages.objects.get(id=item_id)
        except:
            item = models.LandingPages()
        items = models.LandingPages.objects.all()
        exist_links = [i.template_page.id for i in items]
        templates = models.Pages.objects.filter(~Q(id__in=exist_links))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/add-landing-page/?item_id=' + item_id + '&'
        return render(request, 'cadmin/add-landing-page.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'item': item, 
                      'templates': templates, 'success': success, 'error': error })

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        template_page_id = request.POST.get('template_page_id', '').strip()
        personalized_link = request.POST.get('personalized_link', '').strip()
        error = {}
        if check_link(personalized_link, item_id, 'LandingPages'):
            error['personalized_link'] = 'That link is already using by other link, please check and try again.' 
            return self.get(request, '', error)
        redirection_type = request.POST.get('redirection_type', '302 Temporary').strip()
        template_page = models.Pages.objects.get(id=template_page_id)
        try:
            item = models.LandingPages.objects.get(id=item_id)
            success = 'Landing page updated.'
        except:
            item = models.LandingPages()
            success = 'Landing page added.'
        item.template_page = template_page
        item.personalized_link = personalized_link
        item.redirection_type = redirection_type
        item.created_at = datetime.now()
        item.save()
        error = ''
        return self.get(request, success, error)


def check_link(link, item_id, table):
    item_landing = table == 'LandingPages' and models.LandingPages.objects.filter(Q(personalized_link=link), ~Q(id=item_id)).count() if item_id != 'None' else False
    item_pers = table == 'PersLinks' and models.PersLinks.objects.filter(Q(personalized_link=link), ~Q(id=item_id)).count() if item_id != 'None' else False
    item_redirect = table == 'RedirectionLinks' and models.RedirectionLinks.objects.filter(Q(new_link=link), ~Q(id=item_id)).count() if item_id != 'None' else False
    total_landing = models.LandingPages.objects.filter(personalized_link=link).count()
    total_pers = models.PersLinks.objects.filter(personalized_link=link).count()
    total_redirect = models.RedirectionLinks.objects.filter(new_link=link).count()

    if item_id != 'None':
        if item_landing or total_pers or total_redirect:
            return True
        if item_pers or total_landing or total_redirect:
            return True
        if item_redirect or total_landing or total_pers:
            return True
    else:
        if total_landing or total_pers or total_redirect:
            return True
    return False


@method_decorator(admin_login_required, name='dispatch')
class AddPersLinkView(View):

    def get(self, request, success='', error=''):
        item_id = request.GET.get('item_id', '').strip()
        delete_id = request.GET.get('delete_id', '').strip()
        if delete_id:
            models.PersLinks.objects.get(id=delete_id).delete()
            success = 'Personalized deleted.'
        try:
            item = models.PersLinks.objects.get(id=item_id)
        except:
            item = models.PersLinks()
        items = models.PersLinks.objects.all()
        exist_links = [i.landing_page.id for i in items]
        landings = models.LandingPages.objects.filter(~Q(id__in=exist_links))
        users = models.Users.objects.all()
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/add-pers-link/?item_id=' + item_id + '&'
        return render(request, 'cadmin/add-pers-link.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'item': item, 
                      'landings': landings, 'users': users, 'success': success, 'error': error })

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        landing_page_id = request.POST.get('landing_page_id', '').strip()
        personalized_link = request.POST.get('personalized_link', '').strip()
        error = {}
        if check_link(personalized_link, item_id, 'PersLinks'):
            error['personalized_link'] = 'That link is already using by other link, please check and try again.' 
            return self.get(request, '', error)
        assigned_to_user_id = request.POST.get('assigned_to_user_id', '').strip()
        landing_page = models.LandingPages.objects.get(id=landing_page_id)
        # assigned_to_user = models.Users.objects.get(username=assigned_to_user_id)
        try:
            item = models.PersLinks.objects.get(id=item_id)
            success = 'Personalized link updated.'
        except:
            item = models.PersLinks()
            item.created_at = datetime.now()
            item.leads = 0
            success = 'Personalized link added.'
        item.landing_page = landing_page
        item.personalized_link = personalized_link
        item.assigned_to_user = assigned_to_user_id
        item.leads = item.leads
        item.save()
        error = ''
        return self.get(request, success, error)


@method_decorator(admin_login_required, name='dispatch')
class AddRedirectionLinkView(View):

    def get(self, request, success='', error=''):
        item_id = request.GET.get('item_id', '').strip()
        delete_id = request.GET.get('delete_id', '').strip()
        if delete_id:
            models.RedirectionLinks.objects.get(id=delete_id).delete()
            success = 'Redirection link deleted.'
        try:
            item = models.RedirectionLinks.objects.get(id=item_id)
        except:
            item = models.RedirectionLinks()
        items = models.RedirectionLinks.objects.all()
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/add-redirection-link/?item_id=' + item_id + '&'
        return render(request, 'cadmin/add-redirection-link.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'item': item, 
                        'success': success, 'error': error })

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        old_link = request.POST.get('old_link', '').strip()
        new_link = request.POST.get('new_link', '').strip()
        error = {}
        if check_link(new_link, item_id, 'RedirectionLinks'):
            error['new_link'] = 'That link is already using by other link, please check and try again.' 
            return self.get(request, '', error)
        redirection_type = request.POST.get('redirection_type', '302 Temporary').strip()
        try:
            item = models.RedirectionLinks.objects.get(id=item_id)
            success = 'Redirection link updated.'
        except:
            item = models.RedirectionLinks()
            item.created_at = datetime.now()
            success = 'Redirection link added.'
        item.old_link = old_link
        item.new_link = new_link
        item.redirection_type = redirection_type
        item.save()
        error = ''
        return self.get(request, success, error)


def go_page(request, link):
    try:
        redirection_link = models.RedirectionLinks.objects.get(new_link=link)
        cur_link = redirection_link.old_link
    except:
        cur_link = link
    
    try:
        personalized_link = models.PersLinks.objects.get(personalized_link=cur_link)
        page = personalized_link.landing_page.template_page
    except:
        try:
            page = models.LandingPages.objects.get(personalized_link=cur_link).template_page
        except:
            return render(request, 'theme/404-error.html', {})
    
    return return_custom_page(request, page)


def return_custom_page(request, item):
    page_id = item.id
    items = models.Options.objects.filter(((Q(option_type='seo') | Q(option_type='robots_txt')) and Q(option_param1=page_id)) | Q(option_type='header_footer'))
    options = query_set_to_array_option(items)
    print(options)
    return render(request, 'cadmin/custom-page.html', {'item': item, 'options': options})


@method_decorator(admin_login_required, name='dispatch')
class DocumentationsView(View):

    def get(self, request):
        return render(request, 'cadmin/documentations.html', {})


@method_decorator(admin_login_required, name='dispatch')
class PostIssueView(View):

    def get(self, request):
        return render(request, 'cadmin/post-issue.html', {})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        attached_files = request.POST.get('attached_files', '').strip()
        try:
            item = models.Issues.objects.get(id=item_id)
        except:
            item = models.Issues()
            item.created_at = datetime.now()
        
        item.title = title
        item.description = description
        item.attached_files = attached_files
        item.save()
        return render(request, 'cadmin/post-issue.html', {'item': item, 'success': 'Issue Posted'})


@method_decorator(admin_login_required, name='dispatch')
class SeoView(View):

    def get(self, request, success='', error=''):
        page_id = request.GET.get('page_id', '').strip()
        items = models.Options.objects.filter(Q(option_type='seo', option_param1=page_id) | Q(option_type='seo', option_field='robots_txt'))
        items = query_set_to_array_option(items)
        pages = models.Pages.objects.all()
        return render(request, 'cadmin/seo.html', {'items': items, 'pages': pages, 'page_id': page_id, 'success': success, 'error': error})

    def post(self, request):
        if not update_or_create_option(request):
            return self.get(request, error='Not saved')
        return self.get(request, success='Saved')


def query_set_to_array_option(items):
    values = {}
    for item in items:
        if item.option_type not in values:
            values[item.option_type] = {}
        if item.option_param1:
            if item.option_field not in values[item.option_type]:
                values[item.option_type][item.option_field] = {}
            if item.option_param2:
                if item.option_param1 not in values[item.option_type][item.option_field]:
                    values[item.option_type][item.option_field][item.option_param1] = {}
                if item.option_param3:
                    if item.option_param2 not in values[item.option_type][item.option_field][item.option_param1]:
                        values[item.option_type][item.option_field][item.option_param1][item.option_param2] = {}
                    values[item.option_type][item.option_field][item.option_param1][item.option_param2][item.option_param3] = item.option_value
                else: 
                    values[item.option_type][item.option_field][item.option_param1][item.option_param2] = item.option_value
            else: 
                values[item.option_type][item.option_field][item.option_param1] = item.option_value
        else: 
            values[item.option_type][item.option_field] = item.option_value
    return values


def update_or_create_option(request):
    forms = request.POST.items()
    success = True
    for form in forms:
        if len(form[0].split('.')) < 2:
            continue
        option_type = (form[0]).split('.')[0]
        option_field = (form[0]).split('.')[1]
        option_value = (form[1])
        option_param1 = (form[0]).split('.')[2] if len((form[0]).split('.')) > 2 else None
        option_param2 = (form[0]).split('.')[3] if len((form[0]).split('.')) > 3 else None
        option_param3 = (form[0]).split('.')[4] if len((form[0]).split('.')) > 4 else None
        obj, created = models.Options.objects.update_or_create(
            option_type=option_type, option_field=option_field, option_param1=option_param1,
            option_param2=option_param2, option_param3=option_param3, defaults={ "option_value": option_value, })
        # if not created:
        #     success = False
    return success


def get_last_nth_date(day, nth):
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=nth)
    end = dt
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

@method_decorator(admin_login_required, name='dispatch')
class SecurityStatusView(View):

    def get(self, request):
        server_status = True
        startweek, endweek = get_last_nth_date(datetime.now().date().strftime("%Y-%m-%d"), 7)
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.SecurityStatus.objects.values('ip_address', 'user__username').annotate(number_of_attempts=Count('id')).filter(created_at__date__range=(start_date, end_date))
        return render(request, 'cadmin/security-status.html', {'items': items, 'server_status': server_status})


@method_decorator(admin_login_required, name='dispatch')
class OptionsView(View):

    def get(self, request, nav='', success='', error=''):
        items = models.Options.objects.filter(~Q(option_type__in=['seo','robots_txt']))
        items = query_set_to_array_option(items)
        pages = models.Pages.objects.all()
        return render(request, 'cadmin/options.html', {'items': items, 'success': success, 'error': error, 'nav': nav})

    def post(self, request, nav='', success='Saved', error=''):
        if not update_or_create_option(request):
            error={'normal': 'Not saved'}
            success = ''
            return self.get(request, nav, success, error)
        return self.get(request, nav, success, error)


@method_decorator(admin_login_required, name='dispatch')
class OptionsRouterBlogView(View):

    def post(self, request):
        if not update_or_create_option(request):
            return OptionsView.as_view()(request, 'router', '', {'blog': 'Not blog saved'})
        return OptionsView.as_view()(request, 'router', 'Saved')


@method_decorator(admin_login_required, name='dispatch')
class OptionsRouterForgotPasswordView(View):

    def post(self, request):
        if not update_or_create_option(request):
            return OptionsView.as_view()(request, 'router', '', {'forgot_password': 'Not forgot_password saved'})
        return OptionsView.as_view()(request, 'router', 'Saved')


@method_decorator(admin_login_required, name='dispatch')
class CampaignsView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.Campaigns.objects.filter(campaign_name__icontains=search, updated_on__range=(start_date, end_date))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/campaigns/?search=' + search + "&start_date=" + start_date + "&end_date=" + end_date + "&"
        return render(request, 'cadmin/campaigns.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 
                      'start_date': start_date, 'end_date': end_date})


@method_decorator(admin_login_required, name='dispatch')
class CampaignUpdatedView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Campaigns()
        try:
            item = models.Campaigns.objects.get(id=item_id)
            title = 'Edit campaign'
        except:
            title = 'Add new campaign'
        return render(request, 'cadmin/campaign-updated.html', {'item': item, 'title': title, 'country_code': COUNTRY_CODE})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        campaign_name = request.POST.get('campaign_name', '').strip()
        campaign_url = request.POST.get('campaign_url', '').strip()
        overview = request.POST.get('overview', '').strip()
        payout = request.POST.get('payout', '')
        campaign_type = request.POST.get('campaign_type', '').strip()
        target_location = request.POST.getlist('target_location[]')
        creative_materials = request.POST.get('creative_materials', '').strip()
        creative_materials = ','.join(creative_materials.split(','))
        try:
            item = models.Campaigns.objects.get(id=item_id)
        except:
            item = models.Campaigns()
            item.created_at = datetime.now()
        
        item.campaign_name = campaign_name
        item.campaign_url = campaign_url
        item.overview = overview
        item.payout = payout
        item.campaign_type = campaign_type
        item.target_location = target_location
        item.creative_materials = creative_materials
        item.updated_on = datetime.now()
        item.save()
        title = 'Edit Camaign'
        return render(request, 'cadmin/campaign-updated.html', {'item': item, 'title': title, 'success': 'Campaign Updated', 'country_code': COUNTRY_CODE})


@method_decorator(admin_login_required, name='dispatch')
class AffiliatesView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.Affiliates.objects.filter(user__email__icontains=search, user__date_joined__range=(start_date, end_date))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/affiliates/?search=' + search + "&start_date=" + start_date + "&end_date=" + end_date + "&"
        return render(request, 'cadmin/affiliates.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 
                      'start_date': start_date, 'end_date': end_date})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Affiliates.objects.get(id=item_id)
        item.status = False
        item.save()
        return JsonResponse({'success': 'Affiliate suspended.', 'content': item.status})


@method_decorator(admin_login_required, name='dispatch')
class AddNewAffiliateView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Affiliates()
        try:
            item = models.Affiliates.objects.get(id=item_id)
            title = 'Edit affiliate'
        except:
            title = 'Add new affiliate'
        return render(request, 'cadmin/add-new-affiliate.html', {'item': item, 'title': title})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        organization = request.POST.get('organization', '').strip()
        address = request.POST.get('address', '').strip()
        postcode = request.POST.get('postcode', '')
        country = request.POST.get('country', '').strip()
        email_address = request.POST.get('email_address', '').strip()
        password = request.POST.get('password', '').strip()
        send_login_details = request.POST.get('send_login_details', '').strip()
        try:
            item = models.Affiliates.objects.get(id=item_id)
            user = item.user
        except:
            user = models.Users()
            user.joined_date = datetime.now()
            item = models.Affiliates(
                user = user.pk()
            )
        if password:
            user.password = make_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.organization = organization
        user.address = address
        user.postcode = postcode
        user.country = country
        user.email = email_address
        user.save()
        item.save()
        title = 'Edit Affiliate'
        if send_login_details == 'on':
            # logger.info("Send user detail email to {}".format(temp_user.username))
            print(user.send_registered_email('affiliates', password))

        return render(request, 'cadmin/add-new-affiliate.html', {'item': item, 'title': title, 'success': 'This issue has been posted'})


@method_decorator(admin_login_required, name='dispatch')
class ReportsView(View):

    def get(self, request):
        campaign = request.GET.get('campaign', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.Reports.objects.filter(campaign_id=campaign, created_at__range=(start_date, end_date))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        campaigns = models.Campaigns.objects.all()
        base_url = app_url+'/reports/?campaign=' + campaign + "&start_date=" + start_date + "&end_date=" + end_date + "&"
        return render(request, 'cadmin/reports.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'campaign': campaign, 'campaigns': campaigns, 
                      'start_date': start_date, 'end_date': end_date})

    def post(self, request):
        item_id = request.POST.get('item_id', '').strip()
        item = models.Reports.objects.get(id=item_id)
        item.lead_status = False
        item.save()
        return JsonResponse({'success': 'Report rejected.', 'content': 'Rejected'})


@method_decorator(admin_login_required, name='dispatch')
class CommunityPostsView(View):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        items = models.Posts.objects.filter(title__icontains=search, created_at__range=(start_date, end_date))
        page_number = request.GET.get('page', 1)
        items, paginator = do_paginate(items, page_number)
        base_url = app_url+'/community-posts/?search=' + search + "&start_date=" + start_date + "&end_date=" + end_date + "&"
        return render(request, 'cadmin/community-posts.html',
                      {'items': items, 'paginator' : paginator, 'base_url': base_url, 'search': search, 
                      'start_date': start_date, 'end_date': end_date})


@method_decorator(admin_login_required, name='dispatch')
class CommunityPostDetailsView(View):

    def get(self, request):
        item_id = request.GET.get('item_id', '').strip()
        item = models.Posts.objects.get(id=item_id)
        return render(request, 'cadmin/community-post-details.html', {'item': item, })

@method_decorator(admin_login_required, name='dispatch')
class CommunityPostRulesView(View):

    def get(self, request, success='', error=''):
        items = models.Options.objects.filter(option_type='community')
        items = query_set_to_array_option(items)
        return render(request, 'cadmin/community-post-rules.html', {'items': items, 'success': success, 'error': error})

    def post(self, request):
        if not update_or_create_option(request):
            return self.get(request, '', 'Not saved')
        return self.get(request, 'Saved')
