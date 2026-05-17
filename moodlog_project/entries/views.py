from django.db.models import Count
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import EmotionLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import TruncMonth
import calendar
from datetime import datetime

# Create your views here.

class EmotionListView(LoginRequiredMixin, ListView):
    model = EmotionLog
    template_name = 'entries/index.html'
    context_object_name = 'logs'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now()
        year = today.year
        month = today.month

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(year, month)

        user_logs = EmotionLog.objects.filter(
            user=self.request.user,
            created_at__year=year,
            created_at__month=month
        )
        logs_dict = {log.created_at.day: log for log in user_logs}

        context['calendar'] = month_days
        context['logs_dict'] = logs_dict
        context['today'] = today
        return context


class EmotionCreateView(LoginRequiredMixin, CreateView):
    model = EmotionLog
    template_name = 'entries/emotionlog_form.html'
    fields = ['emotion', 'category', 'custom_category', 'note']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
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

        stats = (
            user_logs.annotate(month=TruncMonth('created_at'))
            .values('month', 'emotion')
            .annotate(total=Count('id'))
            .order_by('-month', 'emotion')
        )

        choices = dict(EmotionLog.EMOTION_CHOICES)

        for item in stats:
            full_display = str(choices.get(item['emotion'], "? Unknown"))
            item['display'] = full_display
            item['emoji'] = full_display[0] if len(full_display) > 0 else ""
            item['label'] = full_display[2:] if len(full_display) > 2 else ""

        
        context['monthly_stats'] = stats
        context['total_count'] = user_logs.count()
        return context
    
