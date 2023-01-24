from django.urls import path
from orders.views import OrderView


app_name = "orders"
urlpatterns = [
	path('', OrderView.as_view(), name='order-view'),
]