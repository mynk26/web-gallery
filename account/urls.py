from django.urls import path
from .views import Index,LoginView,SignupView,HomeView, Logout, MainPage

urlpatterns = [
    path('',Index.as_view()),
    path('signup/',SignupView.as_view()),
    path('login/',LoginView.as_view()),
    path('home/',HomeView.as_view()),
    path('logout/',Logout.as_view()),
    path('MainPage/',MainPage.as_view()),
]