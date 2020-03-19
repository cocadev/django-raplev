import json
import random
from datetime import datetime, timedelta, date

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView
from django.utils.crypto import get_random_string
from rest_framework.serializers import ValidationError

from cadmin import models, serializers
from django.http import JsonResponse, HttpResponse
from loremipsum import get_sentence
from slugify import slugify
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Sum, Count, F
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Token
from rest_framework.response import Response

from raplev import settings
from django.core.files.storage import FileSystemStorage


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user, name=request.POST.get('sname'))
        return Response({'token': token.key, 'id': token.user_id, 'username': user.username, 'fullname': user.get_fullname(), 'email': user.email})


class Password(APIView):
    def post(self, request, format=None):
        email = request.POST.get('email', '').strip()
        AFFILIATES_URL = settings.AFFILIATES_URL
        try:
            user = models.Users.objects.get(email=email)
            user.send_recover_email("affiliates")
            return JsonResponse({'success': True}, status = 200)
        except Exception as e:
            return JsonResponse({'success': True}, status = 200)
            # return JsonResponse({'non_field_errors': 'Please provide correct credential info.'}, status=500)


class Reset(APIView):
    def post(self, request):
        password = request.POST.get('password', '').strip()
        token = request.POST.get('token', '').strip()

        try:
            user = models.Users.objects.get(token=token)
            now = datetime.utcnow().timestamp()
            expiration_time = int(token[80:], 0)/10000
            if expiration_time < now:
                return JsonResponse({'non_field_errors': 'Sorry this request is expired. Try again.'}, status=500)

            user.email_verified = True
            user.password = make_password(password)
            user.save()
            return JsonResponse({'success': True}, status = 200)
        except Exception as e:
            print(e)
            return JsonResponse({'non_field_errors': 'Please provide correnct credential info.'}, status=500)
        

class Logout(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        request.auth.delete()
        return Response('success', status=status.HTTP_200_OK)


class FakePost(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        item = models.Posts()
        item.created_at = datetime.now()
        item.posted_by = models.Users.objects.order_by('?').first()
        item.status =  'Publish'
        item.title = get_sentence(1)
        item.context = get_sentence(5)
        item.disallow_comments = False
        item.updated_on = datetime.now()
        item.save()
        return JsonResponse({'id': item.id, 'posted_by': item.posted_by.username, 'title': item.title, 'context': item.context})


class FakeComment(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        print(request.user.id)
        item = models.Comments()
        item.post = models.Posts.objects.get(id=request.GET.get('p')) if request.GET.get('p') else models.Posts.objects.order_by('?').first()
        item.comment = models.Comments.objects.order_by('?').first() if random.random()<0.3 else None
        item.message = get_sentence(1)
        item.created_by = models.Users.objects.order_by('?').first()
        item.created_at = datetime.now()
        item.save()
        return JsonResponse({'id': item.id, 'post_id': item.post.id, 'comment': item.comment.id if item.comment else '', 'message': item.message})


class CommunityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    template = 'apis/pagination/numbers.html'

    def get_paginated_response(self, data):
        return Response({
            'get_html_context': self.get_html_context(),
            'to_html': self.to_html(),
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'results': data
        })


class PostList(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.PostsSerializer
    pagination_class = CommunityPagination
    search = None
    type = None
    user = None

    def get(self, request, *args, **kwargs):
        self.search = request.GET.get('s', '')
        self.type = request.GET.get('t', '')
        self.user = request.user
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        if self.type == 'new':
            return models.Posts.objects.filter(status='Publish').order_by('-updated_on')

        if self.type == 'top':
            queryset = models.Posts.objects.filter(status='Publish').order_by('-updated_on')
            queryset_ids = [item.id for item in queryset if item.upvotes_count > 0]
            queryset = queryset.filter(id__in=queryset_ids)
            return queryset

        if self.type == 'search':
            return models.Posts.objects.filter(status='Publish', title__icontains=self.search).order_by('-updated_on')

        if self.type == 'my':
            return models.Posts.objects.filter(status='Publish', posted_by=self.user).order_by('-updated_on')

        return models.Posts.objects.filter(status='Publish').order_by('-updated_on')

    def perform_create(self, serializer):
        serializer.save(created_at=datetime.now())
        serializer.save(posted_by=self.request.user)
        serializer.save(slug=slugify(serializer.validated_data['title']))


class PostDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = models.Posts.objects.all()
    serializer_class = serializers.PostsSerializer

    def put(self, request, *args, **kwargs):
        if self.request.user != self.get_object().posted_by:
            return JsonResponse({'non_field_errors': 'You can`t change this post.'}, status=500)
        return self.update(request, *args, **kwargs)


class CommunityLimitOffset(LimitOffsetPagination):
    default_limit = 10
    max_limit = 1000
    # template = 'apis/pagination/numbers.html'


class CommentList(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.CommentsSerializer
    pagination_class = CommunityLimitOffset
    post_id = None

    def get(self, request, *args, **kwargs):
        self.post_id = request.GET.get('p', '')
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return models.Comments.objects.filter(post_id=self.post_id, comment=None).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)
        post = models.Posts.objects.get(id=self.request.data['post_id'])
        if models.Comments.objects.filter(post=post, created_by=user, comment=None).count() > 0:
            raise ValidationError('You commented to this post already.')
        else:
            serializer.save(post=post)
        # serializer.save(post=models.Comments.objects.get(id=self.request.data.comment_id))


class CommentDetail(RetrieveUpdateDestroyAPIView):
    queryset = models.Comments.objects.all()
    serializer_class = serializers.CommentsSerializer


class AffiliatesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    template = 'affiliates/pagination/numbers.html'

    def get_paginated_response(self, data):
        return Response({
            'get_html_context': self.get_html_context(),
            'to_html': self.to_html(),
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'results': data
        })


class ListCampaign(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CampaignsSerializer
    user = None

    def get(self, request, *args, **kwargs):
        self.user = request.user.affiliate()
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return models.Campaigns.objects.filter(owner=self.user)


class CampaignList(ListAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.CampaignsSerializer
    pagination_class = AffiliatesPagination
    start_date = None
    end_date = None
    user = None

    def get(self, request, *args, **kwargs):
        self.start_date = request.GET.get('start_date', '')
        self.end_date = request.GET.get('end_date', '')
        self.user = request.user.affiliate()
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return models.Campaigns.objects.filter(owner=self.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            if self.start_date and self.end_date:
                for item in serializer.data:
                    item_id = item['id']
                    item.update({'payouts': models.Reports.objects.filter(campaign_id=item_id, created_at__range=(self.start_date, self.end_date)).aggregate(Sum('payout'))['payout__sum'] or 0})
                    item.update({'clicks': models.Reports.objects.filter(campaign_id=item_id, report_field='click', created_at__range=(self.start_date, self.end_date)).count()})
                    item.update({'conversions': models.Reports.objects.filter(campaign_id=item_id, report_field='conversion', created_at__range=(self.start_date, self.end_date)).count()})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CampaignDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = models.Campaigns.objects.all()
    serializer_class = serializers.CampaignsSerializer


class ReportList(ListAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.ReportsSerializer
    pagination_class = AffiliatesPagination
    start_date = None
    end_date = None
    user = None
    campaign = None

    def get(self, request, *args, **kwargs):
        self.start_date = request.GET.get('start_date', '')
        self.end_date = request.GET.get('end_date', '')
        self.user = request.user.affiliate()
        self.campaign = request.GET.get('campaign', '')
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        if self.campaign:
            items = models.Reports.objects.filter(campaign_id=self.campaign, created_at__range=(self.start_date, self.end_date))
        else:
            items = models.Reports.objects.filter(campaign__owner=self.user, created_at__range=(self.start_date, self.end_date))
        return items


class AffiliatesDashboard(ListAPIView):

    def get(self, request):
        search = request.GET.get('search', '').strip()
        startweek, endweek = get_weekdate(datetime.now().date().strftime("%Y-%m-%d"))
        start_date = request.GET.get('start_date', startweek).strip()
        end_date = request.GET.get('end_date', endweek).strip()
        yesterday = (date.today() - timedelta(days=1))
        yesterday = yesterday.strftime('%Y-%m-%d')
        today = models.Reports.objects.filter(campaign__owner=request.user.affiliate(), created_at__date=date.today()).aggregate(Sum('payout'))['payout__sum'] or 0
        yesterday = models.Reports.objects.filter(campaign__owner=request.user.affiliate(), created_at__date=yesterday).aggregate(Sum('payout'))['payout__sum'] or 0
        week = models.Reports.objects.filter(campaign__owner=request.user.affiliate(), created_at__range=(start_date, end_date)).aggregate(Sum('payout'))['payout__sum'] or 0
        total = models.Reports.objects.filter(campaign__owner=request.user.affiliate()).aggregate(Sum('payout'))['payout__sum'] or 0
        return Response({'today_earned': today, 'yesterday_earned': yesterday, 'week_earned': week, 'total_earned': total})


def get_weekdate(day):
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


class Contact(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.ContactsSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_at=datetime.now())
        serializer.save(subject='Affiliates Contact')
        serializer.save(fullname=user.fullname)
        serializer.save(ip_address=get_client_ip(self.request))
        serializer.save(user=user)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class Request(CreateAPIView):
    serializer_class = serializers.UsersSerializer
    rand_password = ''

    def perform_create(self, serializer):
        serializer.save(username="user" + str(round(datetime.now().timestamp())))
        self.rand_password = get_random_string(length=10)
        serializer.save(password=make_password(self.rand_password))
        serializer.save(created_at=datetime.now())

    def create(self, validated_data):
        res = super().create(validated_data)
        if res.data['id']:
            affiliate = models.Affiliates(
                user_id = res.data['id']
            )
            affiliate.save()
            affiliate.send_requested_email('affiliates')
        return res


class Profile(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.UsersSerializer
    queryset = models.Users.objects.all()

    def get_object(self):
        self.kwargs['pk'] = self.request.user.id

        return super(Profile, self).get_object()

    def perform_update(self, serializer):
        if 'checkbox' in self.request.data and self.request.data['checkbox'] == 'on':
            serializer.save(password=make_password(serializer.validated_data['password']))


class TradeList(ListAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.TradesSerializer

    def get_queryset(self):
        customer = self.request.user.customer()
        return models.Trades.objects.filter(Q(status="archived"), Q(proof_opened=False), Q(payment_method__icontains="_gc"), Q(Q(vendor=customer) | Q(offer__created_by=customer)))


class TradeToken(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        trade_id = request.POST.get('trade_id')
        try:
            trade = models.Trades.objects.get(id=trade_id)
            if trade.seller().user == request.user or trade.buyer().user == request.user:
                new_file = models.Medias(
                    created_by=request.user,
                    created_at=datetime.now()
                )
                new_file.save()
                proof_documents = trade.proof_documents if trade.proof_documents else ''
                proof_documents = [x.strip() for x in (proof_documents + str(new_file.pk)).split(',')]
                trade.proof_documents = ','.join(proof_documents)
                trade.save()
                return Response({'file_id': new_file.pk})
            else:
                return Response({'non_field_errors': 'Invalid trade permission.'}, status=500)
        except Exception as e:
            print(e)
            return Response({'non_field_errors': 'Please provide correct Trade info.'}, status=400)


class SRecorderUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.FILES:
            file_id = request.POST.get('file_id')
            media = models.Medias.objects.get(id=file_id)

            recoder_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(recoder_file.name, recoder_file)
            media.file = filename
            media.save()
            # uploaded_file_url = fs.url(filename)
            return Response({'is_valid': True, 'name': media.file.name, 'url': media.file.url, 'id': media.pk})
        else:
            return Response({'is_valid': False, 'non_field_errors': 'Invalid file upload request.'}, status=500)
