from rest_framework import serializers
from authentication_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'location']
        


class RegistrationSerializer(serializers.ModelSerializer):

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'repeated_password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):

        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']

        if password != repeated_password:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        account = User(email=self.validated_data['email'],
                       username=self.validated_data['username'])
        
        account.set_password(password)
        account.save()
        return account
    

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value