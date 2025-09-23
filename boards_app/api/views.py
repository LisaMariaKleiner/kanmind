from django.db.models import Q
from django.contrib.auth.models import User

from django.http import Http404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, permissions, status

from boards_app.api.permissions import IsBoardOwner, IsBoardOwnerOrMember
from boards_app.models import Board
from .serializers import BoardDetailSerializer, BoardListSerializer, BoardSerializer


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
        if not request.user or not request.user.is_authenticated:
            return Response(
            {'detail': 'Nicht autorisiert. Der Benutzer muss eingeloggt sein.'},
            status=401
        )
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                board = self.get_queryset().get(pk=serializer.data['id'])
                data = BoardListSerializer(board).data
                return Response(data, status=201)
            else:
                # Gebe die tatsächlichen Fehlerdetails zurück
                return Response(
                    {'detail': 'Ungültige Anfragedaten.', 'errors': serializer.errors}, 
                    status=400
                )
            
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=500)
    
    def list(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'detail': 'Nicht autorisiert. Der Benutzer muss eingeloggt sein.'},
                status=401
            )
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = BoardListSerializer(queryset, many=True)
            return Response(serializer.data, status=200)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=500)



class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API-Endpoint für Details, Bearbeiten und Löschen eines Boards.
    GET/PATCH: Owner oder Member.
    DELETE: Nur Owner.
    """
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BoardSerializer  
        return BoardDetailSerializer
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsBoardOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def retrieve(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return self._unauthorized()
        try:
            board_id = kwargs.get('pk')
            try:
                instance = Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                return self._not_found()
            user = request.user
            if not (user == instance.owner or user in instance.members.all()):
                return self._forbidden()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=200)
        except Exception:
            return self._server_error()


    def partial_update(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return self._unauthorized()
        try:
            board_id = kwargs.get('pk')
            board = Board.objects.get(pk=board_id)
            user = request.user
            if not (user == board.owner or user in board.members.all()):
                return self._forbidden()
            serializer = BoardSerializer(board, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # Board komplett neu laden, damit alle Relationen aktuell sind
                board = Board.objects.get(pk=board_id)
                detail_serializer = BoardDetailSerializer(board)
                response_data = {
                    "id": detail_serializer.data["id"],
                    "title": detail_serializer.data["title"],
                    "owner_data": detail_serializer.data["owner_data"],
                    "members_data": detail_serializer.data["members_data"],
                }
                return Response(response_data, status=200)
            else:
                return self._bad_request()
        except Board.DoesNotExist:
            return self._not_found()
        except Exception as e:
            # Fehlerausgabe für Debugging
            return Response({'detail': f'Interner Serverfehler: {str(e)}'}, status=500)


    def destroy(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return self._unauthorized()
        try:
            board_id = kwargs.get('pk')
            board = Board.objects.get(pk=board_id)
            user = request.user
            if user != board.owner:
                return self._forbidden()
            self.perform_destroy(board)
            return Response({'detail': 'Das Board wurde erfolgreich gelöscht.'}, status=204)
        except Board.DoesNotExist:
            return self._not_found()
        except Exception:
            return self._server_error()

    def _unauthorized(self):
        return Response(
            {'detail': 'Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf die Ressource zuzugreifen.'},
            status=401
        )

    def _not_found(self):
        return Response(
            {'detail': 'Board nicht gefunden. Die angegebene Board-ID existiert nicht.'},
            status=404
        )

    def _forbidden(self):
        return Response(
            {'detail': 'Verboten. Der Benutzer muss entweder Mitglied des Boards oder der Eigentümer des Boards sein.'},
            status=403
        )

    def _bad_request(self):
        return Response(
            {'detail': 'Ungültige Anfragedaten. Möglicherweise sind einige Benutzer ungültig.'},
            status=400
        )

    def _server_error(self):
        return Response({'detail': 'Interner Serverfehler.'}, status=500)



class EmailCheckView(generics.GenericAPIView):
    """
    API-Endpoint zur Prüfung, ob eine E-Mail einem registrierten User zugeordnet ist.
    GET: Gibt Userdaten zurück, falls vorhanden.
    """
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'detail': 'Ungültige Anfrage. Die E-Mail-Adresse fehlt.'},
                status=400
            )
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'detail': 'Ungültige Anfrage. Die E-Mail-Adresse hat ein falsches Format.'},
                status=400
            )
        try:
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.username
            }, status=200)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Email nicht gefunden. Die Email existiert nicht.'},
                status=404
            )
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=500)