from django.contrib import admin
from .models import Room, RoomParticipants, Topic, Comment

admin.site.register(Room)
admin.site.register(RoomParticipants)
admin.site.register(Topic)
admin.site.register(Comment)
