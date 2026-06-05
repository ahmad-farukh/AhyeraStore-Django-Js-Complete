from django.contrib import messages

from .models import Notification
from .models import CustomerProfile
from sellers.models import SellerProfile


class NotificationMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            is_seller = False
            try:
                request.user.seller_profile
                is_seller = True
            except SellerProfile.DoesNotExist:
                is_seller = False

            if not is_seller:
                request.user._seller_profile_cache = None
                profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
                request.user._customer_profile_cache = profile

            unread = list(
                Notification.objects.filter(user=request.user, is_read=False)
                .order_by('created_at')[:20]
            )
            if unread:
                for n in unread:
                    messages.info(request, n.message)
                Notification.objects.filter(id__in=[n.id for n in unread]).update(is_read=True)

        return self.get_response(request)
