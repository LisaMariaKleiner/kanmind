"""
URL-Konfiguration für das authentication_app API.

Enthält folgende Endpunkte:
- /profiles/           : Liste und Erstellung von UserProfiles (GET, POST)
- /profiles/<int:pk>/  : Details, Aktualisierung und Löschen eines UserProfiles (GET, PUT/PATCH, DELETE)
- /registration/       : Registrierung eines neuen Benutzers (POST)
- /login/              : Login und Token-Erhalt (POST)
"""

from django.urls import path
from .views import LoginView, UserProfileList, UserProfileDetail
urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('login/', LoginView.as_view(), name='login'), 

]