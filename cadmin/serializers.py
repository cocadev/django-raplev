from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from . import models


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Users
        fields = '__all__'
        extra_kwargs = {'username': {'required': False}, 'password': {'required': False}}


class MediasSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Medias
        fields = ['id', 'file_name', 'file_url', 'created_by_name', 'created_at']


class PostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Posts
        fields = ['id', 'slug', 'title', 'status', 'context', 'tags', 'featured_images', 'disallow_comments', 'updated_on', 'posted_by_name', 'created_at',
            'upvotes_count', 'comments_count', 'get_update_time', 'beauty_context', 'hidden_context']
        extra_kwargs = {'created_at': {'required': False}}

class ThirdSubCommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Comments
        fields = ['id', 'post', 'comment', 'message', 'created_at', 'get_update_time', 'posted_by_name', 'created_at',
            'upvotes_count', 'comments_count', 'get_update_time', 'beauty_context', 'hidden_context']


class SubCommentsSerializer(serializers.ModelSerializer):
    sub_comment_list = ThirdSubCommentsSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.Comments
        fields = ['id', 'post', 'comment', 'message', 'created_at', 'get_update_time', 'posted_by_name', 'created_at',
            'upvotes_count', 'comments_count', 'get_update_time', 'beauty_context', 'hidden_context', 'sub_comment_list']


class CommentsSerializer(serializers.ModelSerializer):
    sub_comment_list = SubCommentsSerializer(many=True, read_only=True)

    class Meta:
        model = models.Comments
        fields = ['id', 'post', 'comment', 'message', 'created_at', 'get_update_time', 'posted_by_name', 'created_at',
            'upvotes_count', 'comments_count', 'get_update_time', 'beauty_context', 'hidden_context', 'sub_comment_list']


class CampaignsSerializer(serializers.ModelSerializer):
    creative_materials_list = serializers.SerializerMethodField()

    class Meta:
        model = models.Campaigns
        fields = ['id', 'campaign_name', 'campaign_url', 'get_status_display', 'overview', 'target_location', 'creative_materials', 'creative_materials_list',
            'updated_on',  'created_at',  'status', 'owner_name', 'get_name', 'total_payouts', 'total_clicks', 'total_conversions']

    def get_creative_materials_list(self, obj):
        return JSONRenderer().render(MediasSerializer(obj.creative_materials_list(), many=True).data)


class ReportsSerializer(serializers.ModelSerializer):
    campaign = CampaignsSerializer(read_only=True)

    class Meta:
        model = models.Reports
        fields = '__all__'


class ContactsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Contacts
        fields = '__all__'
        extra_kwargs = {'created_at': {'required': False}, 'subject': {'required': False}, 'ip_address': {'required': False}}


class TradesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Trades
        fields = ['id', 'message', 'amount', 'created_at', 'trade_price', 'trade_flat', 'trade_payment', 'seller_name', 'buyer_name']
