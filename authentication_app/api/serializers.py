"""
Serializers für das authentication_app API.

- UserProfileSerializer: Serialisiert UserProfile-Objekte für Anzeige und Bearbeitung.
- RegistrationSerializer: Validiert und erstellt neue User-Accounts mit Passwortabgleich und E-Mail-Prüfung.
"""

from rest_framework import serializers
from authentication_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für UserProfile-Objekte.
    Gibt die User-ID, das zugehörige User-Objekt, die Biografie und den Standort aus.
    """
    id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'location']
        


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer für die Registrierung eines neuen Users.

    Felder:
        - fullname: Name des Nutzers (wird als username gespeichert)
        - password: Passwort (write_only)
        - repeated_password: Passwort-Wiederholung (write_only)
        - email: E-Mail-Adresse

    Validierung:
        - Prüft, ob die Passwörter übereinstimmen.
        - Prüft, ob die E-Mail bereits vergeben ist.

    Speicherung:
        - Erstellt einen neuen User mit verschlüsseltem Passwort.
    """
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'password', 'repeated_password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        self._validate_passwords()
        return self._create_user()

    def _validate_passwords(self):
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']
        if password != repeated_password:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

    def _create_user(self):
        fullname = self.validated_data['fullname']
        account = User(
            email=self.validated_data['email'],
            username=fullname
        )
        account.set_password(self.validated_data['password'])
        account.save()
        return account

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value