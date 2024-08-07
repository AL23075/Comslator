from django.db import models
from chat.models import Room
from account.models import User

class VideoCall(models.Model):
#    video_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    room_id  = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField()
    duration   = models.DateTimeField()
    content    = models.TextField()
    is_active  = models.BooleanField(default=True)

class VideoCallParticipants(models.Model):
#    video_call_participants_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey()
    room_id  = models.ForeignKey(Room, on_delete=models.CASCADE)
