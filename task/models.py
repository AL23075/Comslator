from django.db import models
from account.models import User

class Task(models.Model):
#    task_id = models.IntegerField(primary_key=True)
    user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=50)
    content = models.TextField()
    complete = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Schedule(models.Model):
#    schedule_id = models.AutoField(primary_key=True)
    user_id     = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id     = models.ForeignKey(Task, on_delete=models.CASCADE)
    date        = models.DateField()
    time        = models.TimeField()
