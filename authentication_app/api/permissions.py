# Prüft, ob ein User mit einer bestimmten E-Mail existiert (über Query-Parameter 'email')
from django.contrib.auth.models import User
from rest_framework import permissions

class EmailExistsPermission(permissions.BasePermission):
	"""
    Permission-Klasse, die prüft, ob ein User mit einer bestimmten E-Mail existiert.

    Verwendung:
        - Erwartet den Query-Parameter 'email' in der Anfrage.
        - Gibt Zugriff nur frei, wenn ein User mit dieser E-Mail existiert.
        - Setzt eine verständliche Fehlermeldung, falls die E-Mail fehlt oder nicht gefunden wird.
    """
	message = 'Die E-Mail-Adresse existiert nicht.'

	def has_permission(self, request, view):
		email = request.query_params.get('email')
		if not email:
			self.message = 'E-Mail-Parameter fehlt.'
			return False
		if not User.objects.filter(email=email).exists():
			self.message = 'Die E-Mail-Adresse existiert nicht.'
			return False
		return True
