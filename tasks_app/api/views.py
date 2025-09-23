from django.db import models

from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from tasks_app.api.permissions import IsBoardMember, IsCommentAuthor, IsTaskCreatorOrBoardOwner
from tasks_app.models import Task
from .serializers import CommentSerializer, TaskCreateSerializer, TaskListSerializer
from tasks_app.models import Comment



class AssignedTasksListView(generics.ListAPIView):
    """
    Listet alle Tasks, bei denen der User als Bearbeiter oder Prüfer eingetragen ist.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(assignee=user) | models.Q(reviewer=user)
        ).distinct()



class ReviewingTasksListView(generics.ListAPIView):
    """
    Listet alle Tasks, bei denen der User als Prüfer eingetragen ist. 
    """
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)
    


class TaskCreateView(generics.CreateAPIView):
    """
    Erstellt eine neue Task. Nur Board-Mitglieder dürfen Tasks anlegen.
    """
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        board, error = self._get_board(data, user)
        if error:
            return error
        error = self._check_status_priority(data)
        if error:
            return error
        error = self._check_assignee_reviewer(data, board)
        if error:
            return error
        return self._save_task(data, user, board)

    def _get_board(self, data, user):
        from boards_app.models import Board
        board_id = data.get('board')
        if not board_id:
            return None, Response({'detail': 'Board-ID muss angegeben werden.'}, status=400)
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return None, Response({'detail': 'Board nicht gefunden. Das angegebene Board existiert nicht.'}, status=404)
        if not (user == board.owner or user in board.members.all()):
            return None, Response({'detail': 'Verboten. Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen.'}, status=403)
        return board, None

    def _check_status_priority(self, data):
        allowed_status = ['to-do', 'in-progress', 'review', 'done']
        allowed_priority = ['low', 'medium', 'high']
        if data.get('status') not in allowed_status:
            return Response({'detail': f"Ungültiger Status. Erlaubte Werte: {', '.join(allowed_status)}."}, status=400)
        if data.get('priority') not in allowed_priority:
            return Response({'detail': f"Ungültige Priority. Erlaubte Werte: {', '.join(allowed_priority)}."}, status=400)
        return None

    def _check_assignee_reviewer(self, data, board):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for role in ['assignee', 'reviewer']:
            user_id = data.get(f'{role}_id')
            if user_id is not None:
                if not isinstance(user_id, int):
                    try:
                        user_id = int(user_id)
                    except (ValueError, TypeError):
                        return Response({'detail': f'{role.capitalize()} muss eine gültige User-ID (Zahl) sein.'}, status=400)
                try:
                    user_obj = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    return Response({'detail': f'{role.capitalize()} nicht gefunden.'}, status=400)
                if not (user_obj == board.owner or user_obj in board.members.all()):
                    return Response({'detail': f'{role.capitalize()} muss Mitglied des Boards sein.'}, status=400)
                data[role] = user_id
            else:
                data[role] = None
        return None

    def _save_task(self, data, user, board):
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            task = serializer.save(created_by=user, board=board)
            response_serializer = TaskListSerializer(task)
            return Response(response_serializer.data, status=201)
        return Response({'detail': 'Ungültige Anfragedaten.', 'errors': serializer.errors}, status=400)



class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Zeigt Details, erlaubt Bearbeiten und Löschen einer Task.
    Nur Ersteller oder Board-Owner dürfen löschen.
    """
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateSerializer
        return TaskListSerializer
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        valid_fields = set(serializer_class().get_fields().keys())

        for key in request.data.keys():
            if key not in valid_fields:
                return Response(
                    {"detail": f"Ungültiges Feld: '{key}'."},
                    status=400
                )

        return super().update(request, *args, **kwargs)



class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]

    def initial(self, request, *args, **kwargs):
        task_id = self.kwargs['task_id']
        try:
            self.task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task nicht gefunden. Die angegebene Task-ID existiert nicht.")
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return Comment.objects.filter(task=self.task).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, task=self.task)



class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Zeigt Details, erlaubt Bearbeiten und Löschen eines Kommentars.
    Nur der Autor darf löschen, Board-Mitglieder dürfen anzeigen/bearbeiten.
    """
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsCommentAuthor()]
        return [permissions.IsAuthenticated(), IsBoardMember()]

    def get_object(self):
        task_id = self.kwargs['task_id']
        comment_id = self.kwargs['comment_id']
        try:
            return Comment.objects.get(pk=comment_id, task__id=task_id)
        except Comment.DoesNotExist:
            raise NotFound("Kommentar oder Task nicht gefunden.")
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)