from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=300, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="liked")

    def __str__(self):
        return self.user.username
    
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ManyToManyField(User, blank=True, related_name="follower")
    following = models.ManyToManyField(User, blank=True, related_name="following")

    def __str__(self):
        return self.user.username