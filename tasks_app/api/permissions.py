from rest_framework import permissions


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Erlaubt das Löschen einer Task nur, wenn der anfragende User
    entweder der Ersteller (created_by) der Task oder der Owner des Boards ist.
    """

    def has_object_permission(self, request, view, obj):
        # Annahme: Task hat ein Feld 'created_by', das beim Erstellen gesetzt wird
        return (
            obj.created_by == request.user or
            obj.board.owner == request.user
        )
    

class IsBoardMember(permissions.BasePermission):
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
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user