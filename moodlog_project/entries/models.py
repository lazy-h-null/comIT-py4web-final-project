from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class EmotionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    EMOTION_CHOICES = [
        ('HAPPY', '😁 Happy'),
        ('CALM', '☺️ Calm'),
        ('LONELY', '😔 Lonely'),
        ('SAD', '😭 Sad'),
        ('ANGRY', '🤬 Angry'),
    ]
    emotion = models.CharField(max_length=10, choices=EMOTION_CHOICES)
    mood_score = models.IntegerChoices(default=3)

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

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        local_date = timezone.localtime(self.created_at).strftime('%Y-%m-%d')
        return f"{self.user.username}'s mood on {local_date}"

    @property
    def emotion_emoji(self):
        return self.get_emotion_display().split(' ')[0]
    
    @property
    def emotion_label(self):
        parts = self.get_emotion_display().split(' ', 1)
        return parts[1] if len(parts) > 1 else ""