import random
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from entries.models import EmotionLog


def run():
    try:
        user = User.objects.get(username='lazy')
    except User.DoesNotExist:
        print("❗️Error: User 'lazy' not found.")
        return
    
    print("Restoring May 2026...")

    emotions = ['HAPPY', 'CALM', 'LONELY', 'SAD', 'ANGRY']
    categories = ['SELF', 'FAMILY', 'PET', 'FRIENDS', 'WORK', 'OTHER']
    notes_pool = [
        "What a wonderful day",
        "Feeling a bit tired today.",
        "Met some friends and had a great time.",
        "Had too much work to do...",
        "The weather was perfect for a walk.",
        "Just staying home and relaxting.",
        "Thinking about my future.",
        "Delicious food makes me happy!",
        "", "", "", "", "", "", "", ""
        ]

    print("🚀 Test Data generation started (2024 ~ 2026.04)...")

    for day in range(1, 25):
        dt = datetime(2026, 5, day, random.randint(9, 21), 0, 0)
        aware_dt = timezone.make_aware(dt)
        exists = EmotionLog.objects.filter(
            user=user,
            created_at__year=2026,
            created_at__month=5,
            created_at__day=day
        ).exists()
        
        if not exists:
            EmotionLog.objects.create(
                    user=user,
                    emotion=random.choice(emotions),
                    category=random.choice(categories),
                    note=random.choice(notes_pool),
                    created_at=aware_dt
            )

            print(f"✅ May {day} restored.")

        else:
            print(f"May {day} already exists. Skipping.")


    print("✨ Restoration Complete!")

run()

