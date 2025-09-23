from rest_framework import permissions

class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Erlaubt das Löschen einer Task nur, wenn der anfragende User
    entweder der Ersteller (created_by) der Task oder der Owner des Boards ist.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by == request.user or
            obj.board.owner == request.user
        )
    


class IsBoardMember(permissions.BasePermission):
    """
    Erlaubt Aktionen (z.B. Kommentare erstellen), wenn der User Mitglied oder Owner des Boards der Task ist.
    """
    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        from tasks_app.models import Task
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return False
        user = request.user
        board = task.board
        return user == board.owner or user in board.members.all()
    


class IsCommentAuthor(permissions.BasePermission):
    """
    Erlaubt das Löschen/Bearbeiten eines Kommentars nur durch dessen Autor.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
    

def is_board_member_or_owner(user, board):
    """
    Gibt True zurück, wenn der User Owner oder Mitglied des Boards ist.
    """
    return user == board.owner or user in board.members.all()