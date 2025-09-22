from rest_framework import permissions

class IsBoardOwner(permissions.BasePermission):
    """
    Permission-Klasse, die prüft, ob der aktuelle Benutzer der Owner des Boards ist.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    

    
class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Permission-Klasse, die prüft, ob der aktuelle Benutzer Owner oder Mitglied des Boards ist.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()