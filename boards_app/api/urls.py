"""
URL-Konfiguration für das boards_app API.

Enthält folgende Endpunkte:
- /api/boards/                : Liste aller Boards und Erstellen eines neuen Boards (GET, POST)
- /api/boards/<int:pk>/       : Details, Aktualisieren und Löschen eines einzelnen Boards (GET, PATCH/PUT, DELETE)
- /api/boards/email-check/    : Prüft, ob eine E-Mail einem registrierten Benutzer zugeordnet ist (GET, Query-Parameter: email)
"""
from django.urls import path
from .views import BoardDetailView, BoardListCreateView, EmailCheckView

urlpatterns = [
    path('', BoardListCreateView.as_view(), name='board-list-create'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'),   
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]