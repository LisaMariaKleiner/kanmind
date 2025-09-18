from django.db import models
from django.contrib.auth.models import User
from boards_app.models import Board

class Task(models.Model):
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


class Comment(models.Model):
    task = models.ForeignKey('Task', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)