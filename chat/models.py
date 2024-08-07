from django.db import models
from account.models import User

class Topic(models.Model):
#    topic_id   = models.IntegerField(primary_key=True)
    topic_name = models.CharField(max_length=100)

class Room(models.Model):
#    room_id     = models.IntegerField(primary_key=True)
    user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    topic_id    = models.ForeignKey(Topic, on_delete=models.CASCADE)
    room_name   = models.CharField(max_length=50)
    description = models.TextField()
    updated_at  = models.DateTimeField(auto_now=True)
    created_at  = models.DateTimeField(auto_now_add=True)

class RoomParticipants(models.Model):
#    room_participants_id = models.IntegerField(primary_key=True)
    room_id  = models.ForeignKey(Room, on_delete=models.CASCADE)
    user_id     = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
#    comment_id = models.IntegerField(primary_key=True)
    user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    room_id  = models.ForeignKey(Room, on_delete=models.CASCADE)
    creatd_at  = models.DateTimeField(auto_now_add=True)
    content    = models.TextField()

