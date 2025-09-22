"""
URL-Konfiguration für das tasks_app API.

Enthält folgende Endpunkte:
- /api/tasks/                         : Erstellt eine neue Task (POST)
- /api/tasks/<int:pk>/                : Details, Aktualisieren und Löschen einer Task (GET, PATCH/PUT, DELETE)
- /api/tasks/assigned-to-me/          : Listet alle Tasks, bei denen der User Bearbeiter ist (GET)
- /api/tasks/reviewing/               : Listet alle Tasks, bei denen der User Prüfer ist (GET)
- /api/tasks/<int:task_id>/comments/  : Erstellt einen neuen Kommentar zu einer Task (POST)
- /api/tasks/<int:task_id>/comments/<int:comment_id>/ : Details, Aktualisieren und Löschen eines Kommentars (GET, PATCH/PUT, DELETE)
"""
from django.urls import path
from .views import AssignedTasksListView, CommentCreateView, CommentDetailView, ReviewingTasksListView, TaskCreateView, TaskDetailView

urlpatterns = [
    path('assigned-to-me/', AssignedTasksListView.as_view(), name='assigned-to-me'),
    path('reviewing/', ReviewingTasksListView.as_view(), name='reviewing'),
    path('', TaskCreateView.as_view(), name='task-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),  
    path('<int:task_id>/comments/', CommentCreateView.as_view(), name='task-comments'),
    path('<int:task_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='task-comment-detail'),

]