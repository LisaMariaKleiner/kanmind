from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from authentication_app.api.serializers import RegistrationSerializer, UserProfileSerializer
from authentication_app.models import UserProfile


class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
  permission_classes = [AllowAny]

  def post(self, request):
    serializer = RegistrationSerializer(data=request.data)
    saved_account = None 
    data = {}

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
        data = serializer.errors
        status_code = 400

    return Response(data, status=status_code)
  

# Custom Login View to return additional user info
class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email,
                'user_id': user.id
            }
            status_code = 201
        else:
            data = serializer.errors
            status_code = 400

        return Response(data, status=status_code)