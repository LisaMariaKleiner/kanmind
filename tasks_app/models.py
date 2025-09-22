from django.db import models
from django.contrib.auth.models import User
from boards_app.models import Board

class Task(models.Model):
	"""
    Modell für einen Task innerhalb eines Boards.

    Felder:
        - board: Zugehöriges Board (ForeignKey)
        - title: Titel des Tasks
        - description: Beschreibung des Tasks (optional)
        - status: Status des Tasks (to-do, in-progress, review, done)
        - priority: Priorität des Tasks (low, medium, high)
        - assignee: Bearbeiter (User, optional)
        - reviewer: Prüfer (User, optional)
        - due_date: Fälligkeitsdatum (optional)
        - created_by: Ersteller des Tasks

    Zweck:
        Tasks können Boards zugeordnet, verschiedenen Nutzern zugewiesen und mit Status/Priorität versehen werden.
    """
	STATUS_CHOICES = [
		('to-do', 'To Do'),
		('in-progress', 'In Progress'),
		('review', 'Review'),
		('done', 'Done'),
	]
	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High'),
	]

	board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
	assignee = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
	reviewer = models.ForeignKey(User, related_name='reviewed_tasks', on_delete=models.SET_NULL, null=True, blank=True)
	due_date = models.DateField(null=True, blank=True)
	created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)

	def __str__(self):
			return self.title

	class Meta:
			verbose_name = "Task"
			verbose_name_plural = "Tasks"
			ordering = ["-due_date", "priority"]    


class Comment(models.Model):
    """
    Modell für einen Kommentar zu einer Aufgabe.

    Felder:
        - task: Zugehörige Aufgabe (ForeignKey)
        - author: Autor des Kommentars (User)
        - content: Inhalt des Kommentars
        - created_at: Erstellungszeitpunkt

    Zweck:
        Kommentare ermöglichen Diskussionen und Notizen zu einzelnen Aufgaben.
    """

    task = models.ForeignKey('Task', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]