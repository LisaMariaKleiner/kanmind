from django.contrib.auth.models import User
from django.db import models


 
class UserProfile(models.Model):
    """
    UserProfile erweitert das Standard-User-Modell um zusätzliche Profilinformationen.

    Felder:
        user: OneToOne-Verknüpfung zum User-Modell.
        bio: Optionale Biografie des Nutzers.
        location: Optionaler Standort des Nutzers (max. 100 Zeichen).

    Zweck:
        Ermöglicht das Speichern von Zusatzinformationen zu jedem Benutzer,
        ohne das Standard-User-Modell direkt zu verändern.
"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username