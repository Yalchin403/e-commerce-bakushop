
from django.conf import settings


def get_user(request):
    return {
        'user': request.user
    }
