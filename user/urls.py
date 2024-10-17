from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view()),
    path('login/', views.UserLoginView.as_view()),
    path('verify/<str:token>/', views.verify_registered_user,name="verify"),
]