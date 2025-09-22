from rest_framework import generics, permissions, status
from boards_app.api.permissions import IsBoardOwner, IsBoardOwnerOrMember
from boards_app.models import Board
from .serializers import BoardDetailSerializer, BoardListSerializer, BoardSerializer
from django.db.models import Q
from rest_framework.response import Response
from authentication_app.api.permissions import EmailExistsPermission
from django.contrib.auth.models import User


# Verwendet GET für Listenansicht und POST für Erstellung
# Nur eingeloggte Benutzer können Boards sehen und erstellen
# Zeigt alle Boards an, bei denen der Benutzer Eigentümer oder Mitglied ist
# Beim Erstellen wird der Eigentümer automatisch auf den angemeldeten Benutzer gesetzt
class BoardListCreateView(generics.ListCreateAPIView):
    """
    API-Endpoint zum Auflisten und Erstellen von Boards.
    GET: Gibt alle Boards zurück, bei denen der User Owner oder Member ist.
    POST: Erstellt ein neues Board mit dem aktuellen User als Owner.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardListSerializer
        return BoardSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        board = self.get_queryset().get(pk=response.data['id'])
        data = BoardListSerializer(board).data
        return Response(data, status=status.HTTP_201_CREATED)


# Detailansicht, Aktualisierung und Löschung eines Boards
# Nur der Eigentümer kann ein Board löschen
# Mitglieder und Eigentümer können Details anzeigen und bearbeiten
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API-Endpoint für Details, Bearbeiten und Löschen eines Boards.
    GET/PATCH: Owner oder Member.
    DELETE: Nur Owner.
    """
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsBoardOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_update(self, serializer):
        serializer.save()



class EmailCheckView(generics.GenericAPIView):
    """
    API-Endpoint zur Prüfung, ob eine E-Mail einem registrierten User zugeordnet ist.
    GET: Gibt Userdaten zurück, falls vorhanden.
    """
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        user = User.objects.get(email=email)
        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': user.username
        }, status=200)