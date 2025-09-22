from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
	"""
    Modell für ein Board.

    Felder:
        - title: Titel des Boards (max. 255 Zeichen)
        - owner: User, dem das Board gehört (ForeignKey)
        - members: Mitglieder des Boards (ManyToMany zu User)

    Zweck:
        Ein Board dient als Container für Aufgaben (Tasks) und kann von mehreren Benutzern gemeinsam genutzt werden.
        Der Owner ist der Hauptverantwortliche, Mitglieder können gemeinsam arbeiten.
    """
	 
	title = models.CharField(max_length=255)
	owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE)
	members = models.ManyToManyField(User, related_name='boards')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "Board"
		verbose_name_plural = "Boards"
		ordering = ["title"]

