from rest_framework import permissions

# Prüft, ob der angemeldete Benutzer der Eigentümer des Boards ist
class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    
# Prüft, ob der angemeldete Benutzer der Eigentümer oder ein Mitglied des Boards ist
class IsBoardOwnerOrMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()