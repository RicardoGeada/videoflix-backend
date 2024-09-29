from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView

router = DefaultRouter()
# router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    # path('', include(router.urls)),
    # path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register')
]