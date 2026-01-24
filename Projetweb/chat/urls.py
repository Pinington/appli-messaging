from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("home/", views.home, name="home"),
    path('create/', views.create_room, name='create_room'),
    path('send/', views.send_message, name='send_message'),
    path('api/messages/<int:room_id>/', views.get_messages_json, name='get_messages_json'),

    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('ban-user/<int:salon_id>/<int:user_id>/', views.ban_user, name='ban_user'),
    path('delete-salon/<int:salon_id>/', views.delete_salon, name='delete_salon'), 
]