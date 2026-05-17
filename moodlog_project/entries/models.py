from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class EmotionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    EMOTION_CHOICES = [
        ('HAPPY', '😁 Happy'),
        ('CALM', '😌 Calm'),
        ('LONELY', '😔 Lonely'),
        ('SAD', '😭 Sad'),
        ('ANGRY', '🤬 Angry'),
    ]
    emotion = models.CharField(max_length=10, choices=EMOTION_CHOICES)

    CATEGORY_CHOICES = [
        ('SELF', 'Self'),
        ('FAMILY', 'Family'),
        ('PET', 'Pet'),
        ('FRIENDS', 'Friends'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    custom_category = models.CharField(max_length=20, blank=True, null=True)

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s mood on {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def emotion_emoji(self):
        return self.get_emotion_display()[0]
    
    @property
    def emotion_label(self):
        return self.get_emotion_display()[2:]