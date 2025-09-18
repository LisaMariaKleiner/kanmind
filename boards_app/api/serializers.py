from rest_framework import serializers
from boards_app.models import Board
from django.contrib.auth.models import User

# Für POST/PUT (Erstellen/Bearbeiten)
class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members']

# Für GET (Listenansicht)
class BoardListSerializer(serializers.ModelSerializer):
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
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id')
    members = UserShortSerializer(many=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        return []  # Platzhalter, bis das Task-Modell existiert