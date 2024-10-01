from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, ActivateAccount

router = DefaultRouter()

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate_account')
]