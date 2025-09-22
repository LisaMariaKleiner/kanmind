from django.contrib.auth.models import User

from rest_framework import serializers

from tasks_app.models import Task
from boards_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer für das Erstellen und Bearbeiten von Boards.

    Felder:
        - id: Board-ID
        - title: Titel des Boards
        - owner: Eigentümer des Boards (read_only)
        - members: Liste der Mitglieder (User-IDs)
    """
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members']



class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Listenansicht von Boards.

    Felder:
        - id: Board-ID
        - title: Titel des Boards
        - owner_id: User-ID des Eigentümers
        - member_count: Anzahl der Mitglieder
        - ticket_count: Anzahl der Tickets (Platzhalter)
        - tasks_to_do_count: Anzahl offener Tasks (Platzhalter)
        - tasks_high_prio_count: Anzahl Tasks mit hoher Priorität (Platzhalter)
    """
        
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title',  'member_count',
            'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count','owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return 0  # Platzhalter

    def get_tasks_to_do_count(self, obj):
        return 0  # Platzhalter

    def get_tasks_high_prio_count(self, obj):
        return 0  # Platzhalter



class UserShortSerializer(serializers.ModelSerializer):
    """
    Serializer für Kurzinfos eines Users.

    Felder:
        - id: User-ID
        - email: E-Mail-Adresse
        - fullname: Anzeigename (username)
    """
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']



class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer für die Detailansicht eines Boards.

    Felder:
        - id: Board-ID
        - title: Titel des Boards
        - owner_id: User-ID des Eigentümers
        - members: Liste der Mitglieder (als UserShortSerializer)
        - tasks: Liste der Tasks (Platzhalter, bis Task-Modell existiert)
    """
    title = serializers.CharField(required=False)
    owner_id = serializers.IntegerField(source='owner.id')
    members = UserShortSerializer(many=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        from tasks_app.api.serializers import TaskListSerializer  
        tasks = Task.objects.filter(board=obj)
        return TaskListSerializer(tasks, many=True).data