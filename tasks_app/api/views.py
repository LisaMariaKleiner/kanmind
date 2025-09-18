from rest_framework import generics, permissions
from django.db import models
from tasks_app.api.permissions import IsBoardMember, IsCommentAuthor, IsTaskCreatorOrBoardOwner
from tasks_app.models import Task
from .serializers import CommentSerializer, TaskCreateSerializer, TaskListSerializer
from rest_framework.exceptions import NotFound


class AssignedTasksListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(assignee=user) | models.Q(reviewer=user)
        ).distinct()


class ReviewingTasksListView(generics.ListAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)
    

class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
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
    

from tasks_app.models import Comment

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer  
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        from tasks_app.models import Task
        task = Task.objects.get(pk=task_id)
        serializer.save(author=self.request.user, task=task)



class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
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