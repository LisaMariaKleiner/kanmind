from django.contrib.auth.models import User
from rest_framework import serializers
from tasks_app.models import Task
from boards_app.api.serializers import UserShortSerializer
from tasks_app.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer für einen Kommentar zu einer Task.

    Felder:
        - id: Kommentar-ID
        - created_at: Erstellungszeitpunkt
        - author: Name des Autors (username)
        - content: Inhalt des Kommentars
    """
    author = serializers.CharField(source='author.username', read_only=True)
    content = serializers.CharField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']



class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer für Tasks in Listen- und Detailansicht.

    Felder:
        - id, board, title, description, status, priority, due_date
        - assignee: Bearbeiter (UserShortSerializer)
        - reviewer: Prüfer (UserShortSerializer)
        - comments_count: Anzahl der Kommentare
        - comments: Liste der Kommentare (CommentSerializer)
    """
    assignee = UserShortSerializer()
    reviewer = UserShortSerializer()
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count', 'comments'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()




class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer für das Erstellen und Aktualisieren von Tasks.

    Felder:
        - id, board, title, description, status, priority, due_date
        - assignee_id: ID des Bearbeiters (write_only)
        - reviewer_id: ID des Prüfers (write_only)

    Validierung:
        - Prüft, ob der User Mitglied des Boards ist.
        - Prüft, ob assignee/reviewer Mitglieder des Boards sind.
        - Prüft Status und Priorität auf gültige Werte.

    Ausgabe:
        - Gibt assignee, reviewer, comments_count und comments wie in TaskListSerializer aus.
    """
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', required=False, allow_null=True, write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'due_date'
        ]

    def validate(self, data):
        board = data.get('board') or getattr(self.instance, 'board', None)
        self._validate_board(board)
        self._validate_members(board, data)
        self._validate_status_priority(data)
        return data

    def _validate_board(self, board):
        user = self.context['request'].user
        if not board:
            raise serializers.ValidationError("Board ist erforderlich.")
        if not (user == board.owner or user in board.members.all()):
            raise serializers.ValidationError("Du bist kein Mitglied dieses Boards.")

    def _validate_members(self, board, data):
        for role, member in [('assignee', data.get('assignee')), ('reviewer', data.get('reviewer'))]:
            if member and not (member == board.owner or member in board.members.all()):
                raise serializers.ValidationError(f"{role.capitalize()} muss Mitglied des Boards sein.")

    def _validate_status_priority(self, data):
        if 'status' in data and data.get('status') not in ['to-do', 'in-progress', 'review', 'done']:
            raise serializers.ValidationError("Ungültiger Status.")
        if 'priority' in data and data.get('priority') not in ['low', 'medium', 'high']:
            raise serializers.ValidationError("Ungültige Priorität.")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['assignee'] = UserShortSerializer(instance.assignee).data if instance.assignee else None
        rep['reviewer'] = UserShortSerializer(instance.reviewer).data if instance.reviewer else None
        rep['comments_count'] = instance.comments.count()
        rep['comments'] = CommentSerializer(instance.comments, many=True).data
        return rep
