from django.contrib import admin
from .models import Salon, SalonMember, Message

admin.site.register(Salon)
admin.site.register(SalonMember)
admin.site.register(Message)