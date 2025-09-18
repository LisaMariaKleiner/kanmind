from rest_framework import serializers
from authentication_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'location']
        


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'password', 'repeated_password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']
        fullname = self.validated_data['fullname']

        if password != repeated_password:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        account = User(email=self.validated_data['email'],
                       username=fullname)
        
        account.set_password(password)
        account.save()
        return account
    

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value