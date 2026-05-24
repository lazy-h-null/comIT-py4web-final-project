from django.db.models import Count, Case, When, Value, IntegerField
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import EmotionLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import TruncMonth, ExtractMonth
import calendar
from datetime import datetime
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.views.generic.edit import FormView
import json

# Create your views here.

class EmotionListView(LoginRequiredMixin, ListView):
    model = EmotionLog
    template_name = 'entries/index.html'
    context_object_name = 'logs'
    
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        
        today = timezone.localtime(timezone.now())   
        year = int(self.kwargs.get('year', today.year))
        month = int(self.kwargs.get('month', today.month))

        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
        
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(year, month)

        user_logs = EmotionLog.objects.filter(
            user=self.request.user,
            created_at__year=year,
            created_at__month=month
        )
        logs_dict = {timezone.localtime(log.created_at).day: log for log in user_logs}

        is_latest = (year > today.year) or (year == today.year and month >= today.month)

        context.update({
            'calendar': month_days,
            'logs_dict': logs_dict,
            'now': today,
            'view_date': datetime(year, month, 1),
            'prev_year': prev_year,
            'next_year': next_year,
            'prev_month': prev_month,
            'next_month': next_month,
            'is_latest': is_latest,
        })

        return context


class EmotionCreateView(LoginRequiredMixin, CreateView):
    model = EmotionLog
    template_name = 'entries/emotionlog_form.html'
    fields = ['emotion', 'category', 'custom_category', 'note']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        today = timezone.localtime(timezone.now()).date()
        already_exists = EmotionLog.objects.filter(
            user=self.request.user,
            created_at__date=today
        ).exists()

        if already_exists:
            messages.error(self.request, "You have already logged your mood for today! See you tomorrow. 👋")
            return redirect('index')
        
        form.instance.user = self.request.user
        messages.success(self.request, "Today's mood has been recorded successfully!")
        return super().form_valid(form)


class EmotionUpdateView(LoginRequiredMixin, UpdateView):
    model = EmotionLog
    template_name = 'entries/emotionlog_form.html'
    fields = ['emotion', 'category', 'custom_category', 'note']
    success_url = reverse_lazy('index')


class EmotionDeleteView(LoginRequiredMixin, DeleteView):
    model = EmotionLog
    template_name = 'entries/emotionlog_confirm_delete.html'
    success_url = reverse_lazy('index')


class EmotionStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'entries/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_logs = EmotionLog.objects.filter(user=self.request.user)
        
        global_latest = user_logs.order_by('-created_at').first()
        if global_latest:
            latest_year = global_latest.created_at.year
            latest_month = global_latest.created_at.month
        else:
            latest_year = timezone.now().year
            latest_month = timezone.now().month

        years_in_db = sorted(list(set(user_logs.dates('created_at', 'year'))), key=lambda x: x.year)
        years_list = [dt.year for dt in years_in_db]
        view_year = self.kwargs.get('year')
        
        if not view_year:
            view_year = latest_year

        prev_year = next_year = None
        if view_year in years_list:
            idx = years_list.index(view_year)
            if idx > 0: prev_year = years_list[idx -1]
            if idx < len(years_list) - 1: next_year = years_list[idx + 1]

        latest_month_in_year = user_logs.filter(created_at__year=view_year).order_by('-created_at').first()
        view_month = latest_month_in_year.created_at.month if latest_month_in_year else 12
        

        stats = (
            user_logs.filter(created_at__year=latest_year, created_at__month=latest_month)
            .annotate(month=TruncMonth('created_at'))
            .values('month', 'emotion')
            .annotate(total=Count('id'))
            .annotate(
                emotion_order=Case(
                    When(emotion='HAPPY', then=Value(1)),
                    When(emotion='CALM', then=Value(2)),
                    When(emotion='LONELY', then=Value(3)),
                    When(emotion='SAD', then=Value(4)),
                    When(emotion='ANGRY', then=Value(5)),
                    default=Value(6),
                    output_field=IntegerField(),
                )
            )
            .order_by('emotion_order')
        )

        choices = dict(EmotionLog.EMOTION_CHOICES)

        for item in stats:
            full_display = str(choices.get(item['emotion'], "? Unknown"))
            item['display'] = full_display
            parts = full_display.split(' ', 1)
            item['emoji'] = parts[0] if len(parts) > 0 else ""
            item['label'] = parts[1] if len(parts) > 1 else ""

        
        context['monthly_stats'] = stats
        context['total_count'] = user_logs.count()
        context['current_view_month'] = f"{view_year}.{view_month}"
        
        yearly_logs = user_logs.filter(created_at__year=view_year).annotate(month=ExtractMonth('created_at'))

        score_map = {
            'happy': 5,
            'calm': 4,
            'lonely': 3,
            'sad': 2,
            'angry': 1
        }

        monthly_scores = [0] * 12
        monthly_counts = [0] * 12
        
        for log in yearly_logs:
            month_idx = log.month - 1
            score = score_map.get(log.emotion.lower(), 0)
            monthly_scores[month_idx] += score
            monthly_counts[month_idx] += 1

        chart_labels = [
            [calendar.month_name[m][:3].upper(), f"({count})"]
            for m, count in zip(range(1,13), monthly_counts)
        ]

        context.update({
            'monthly_stats': stats,
            'total_count': user_logs.count(),
            'chart_labels': json.dumps(chart_labels),
            'chart_scores': json.dumps(monthly_scores),
            'view_year': view_year,
            'prev_year': prev_year,
            'next_year': next_year,
        })

        return context


class CustomPasswordChangeView(LoginRequiredMixin, FormView):
    form_class = SetPasswordForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been updated successfully!")
        return super().form_valid(form)