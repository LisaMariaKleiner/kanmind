from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication_app.api.permissions import EmailExistsPermission
from authentication_app.api.serializers import LoginSerializer, RegistrationSerializer, UserProfileSerializer
from authentication_app.models import UserProfile


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
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsAuthenticated]


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
  

class LoginView(APIView):
    """
    API-Endpoint für den Login.

    POST:
        Erwartet email und password.
        Gibt bei Erfolg ein Auth-Token und Userdaten zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        data = {}

        try:
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                User = get_user_model()
                try:
                    user_obj = User.objects.get(email=email)
                except User.DoesNotExist:
                    return Response({'detail': 'Ungültige Zugangsdaten.'}, status=400)
                user = authenticate(username=user_obj.username, password=password)
                if user:
                    token, _ = Token.objects.get_or_create(user=user)
                    data = {
                        'token': token.key,
                        'fullname': user.username,
                        'email': user.email,
                        'user_id': user.id,
                    }
                    status_code = 200
                else:
                    data = {'detail': 'Ungültige Zugangsdaten.'}
                    status_code = 400
            else:
                data = {'detail': 'Ungültige Anfragedaten.'}
                status_code = 400
        except Exception:
            data = {'detail': 'Interner Serverfehler.'}
            status_code = 500

        return Response(data, status=status_code)