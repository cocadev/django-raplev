from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'FACEBOOK_LINK': settings.FACEBOOK_LINK,
        'LIKEDIN_LINK': settings.LIKEDIN_LINK,
        'TWITTER_LINK': settings.TWITTER_LINK,
        'YOUTUBE_LINK': settings.YOUTUBE_LINK
    }