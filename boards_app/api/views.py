from rest_framework import generics, permissions, status
from boards_app.models import Board
from .serializers import BoardDetailSerializer, BoardListSerializer, BoardSerializer
from django.db.models import Q
from rest_framework.response import Response


class BoardListCreateView(generics.ListCreateAPIView):
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


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_update(self, serializer):
        serializer.save()