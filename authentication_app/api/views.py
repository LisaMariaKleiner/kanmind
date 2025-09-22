from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication_app.api.permissions import EmailExistsPermission
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from authentication_app.api.serializers import RegistrationSerializer, UserProfileSerializer
from authentication_app.models import UserProfile
from django.contrib.auth.models import User


class UserProfileList(generics.ListCreateAPIView):
    """
    API-Endpoint zum Auflisten und Erstellen von UserProfiles.
    GET:
        Gibt eine Liste aller UserProfile-Objekte zurück.
    POST:
        Erstellt ein neues UserProfile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API-Endpoint zum Abrufen, Aktualisieren und Löschen eines einzelnen UserProfiles.
    GET:
        Gibt die Details eines UserProfiles zurück.
    PUT/PATCH:
        Aktualisiert das UserProfile.
    DELETE:
        Löscht das UserProfile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
    """
    API-Endpoint zur Registrierung eines neuen Benutzers.

    POST:
        Erwartet Benutzerdaten (z.B. username, email, password).
        Gibt bei Erfolg ein Auth-Token und Userdaten zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        try:
            if serializer.is_valid():
                saved_account = serializer.save()
                token, created = Token.objects.get_or_create(user=saved_account)
                data = {
                    'token': token.key,
                    'fullname': saved_account.username,
                    'email': saved_account.email,
                    'user_id': saved_account.id
                }
                status_code = 201
            else:
                data = {'detail': 'Ungültige Anfragedaten.'}
                status_code = 400
        except Exception:
            data = {'detail': 'Interner Serverfehler.'}
            status_code = 500
        return Response(data, status=status_code)
  

class LoginView(ObtainAuthToken):
    """
    API-Endpoint für den Login.

    POST:
        Erwartet username und password.
        Gibt bei Erfolg ein Auth-Token und Userdaten zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}

        try:
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, _ = Token.objects.get_or_create(user=user)
                data = {
                    'token': token.key,
                    'fullname': user.username,
                    'email': user.email,
                    'user_id': user.id,
                }
                status_code = 200
            else:
                data = {'detail': 'Ungültige Anfragedaten.'}
                status_code = 400
        except Exception:
            data = {'detail': 'Interner Serverfehler.'}
            status_code = 500

        return Response(data, status=status_code)