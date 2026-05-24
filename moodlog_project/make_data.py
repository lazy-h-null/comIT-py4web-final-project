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
    
    # print("Cleaning old data...")
    # EmotionLog.objects.filter(user=user).delete()
    # print("Clean up complete!")

    emotions = ['HAPPY', 'CALM', 'LONELY', 'SAD', 'ANGRY']
    categories = ['SELF', 'FAMILY', 'PET', 'FRIENDS', 'WORK', 'OTHER']
    notes_pool = ["Test",""]

    print("🚀 Test Data generation started (2024 ~ 2026.04)...")

    years_config = {
        2024: range(1, 13),
        2025: range(1, 13),
        2026: range(1, 5)
    }

    for year, months in years_config.items():
        for month in months:
            num_logs = random.randint(15, 20)
            days = random.sample(range(1, 29), num_logs)

            for day in days:
                dt = datetime(year, month, day, random.randint(9, 21), 0, 0)
                aware_dt = timezone.make_aware(dt)

                EmotionLog.objects.create(
                    user=user,
                    emotion=random.choice(emotions),
                    category=random.choice(categories),
                    note=random.choice(notes_pool),
                    created_at=aware_dt
                )

        print(f"✅ Success: Month {month} / {num_logs} entries created.")

    print("✨ All data generated! Check in your browser.")

run()

