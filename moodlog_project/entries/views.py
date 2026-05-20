from django.db.models import Count
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import EmotionLog
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import TruncMonth
import calendar
from datetime import datetime
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.views.generic.edit import FormView

# Create your views here.

class EmotionListView(LoginRequiredMixin, ListView):
    model = EmotionLog
    template_name = 'entries/index.html'
    context_object_name = 'logs'
    
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        
        today = timezone.localtime(timezone.now())   
        year = self.kwargs.get('year', today.year)
        month = self.kwargs.get('month', today.month)

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

        context.update({
            'calendar': month_days,
            'logs_dict': logs_dict,
            'now': today,
            'view_date': datetime(year, month, 1),
            'prev_year': prev_year, 'prev_month': prev_month,
            'next_year': next_year, 'next_month': next_month,
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