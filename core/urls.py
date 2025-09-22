from django.contrib import admin
from django.urls import include, path
from authentication_app.api.views import RegistrationView, LoginView
from boards_app.api.views import EmailCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/registration/', RegistrationView.as_view(), name='registration'),  
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/email-check/', EmailCheckView.as_view(), name='email-check'), 
               
    path('api/auth/', include('authentication_app.api.urls')),
    path('api/boards/', include('boards_app.api.urls')),
    path('api/tasks/', include('tasks_app.api.urls')),
]