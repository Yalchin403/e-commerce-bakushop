from django.urls import path
from home.views import (
	HomeView,
	AboutView,
	ContactView,
	SearchView,
	HomeDetailView,
	LogView,
)

app_name = "home"
urlpatterns = [
	path('', HomeView.as_view(), name='home'),
	path('<str:category>/<str:name>/', HomeDetailView.as_view(), name="detail"),
	path('about/', AboutView.as_view(), name="about"),
	path('search/', SearchView.as_view(), name="search"),
	path('contact/', ContactView.as_view(), name='contact'),
	path('log/', LogView.as_view(), name='log'),
]