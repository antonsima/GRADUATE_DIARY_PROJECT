from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import ListView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from datetime import datetime
import calendar

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenRefreshView as SimpleTokenRefreshView

from users.models import User
from .models import Entry, Tag, Mood, Reminder
from .serializers import (
    EntrySerializer, TagSerializer,
    MoodSerializer, ReminderSerializer,
    EntryDetailSerializer, UserProfileSerializer, UserUpdateSerializer, UserRegistrationSerializer, UserLoginSerializer
)
from .permissions import IsOwnerOrReadOnly


class EntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с записями дневника.
    Поддерживает все CRUD операции + кастомные действия.
    """
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """Используем разные сериализаторы для разных действий"""
        if self.action == 'retrieve':
            return EntryDetailSerializer
        return EntrySerializer

    def get_queryset(self):
        """Возвращает только записи текущего пользователя"""
        user = self.request.user
        queryset = Entry.objects.filter(owner=user)

        # Фильтрация по тегам
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()

        # Фильтрация по настроению
        mood = self.request.query_params.get('mood')
        if mood:
            queryset = queryset.filter(mood__name=mood)

        # Фильтрация по дате
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)

        return queryset.order_by('-entry_date')

    def perform_create(self, serializer):
        """Автоматически устанавливаем владельца записи"""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Последние 5 записей"""
        recent_entries = self.get_queryset()[:5]
        serializer = self.get_serializer(recent_entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Записи за конкретную дату"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date parameter required'}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            entries = self.get_queryset().filter(entry_date=date)
            serializer = self.get_serializer(entries, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с тегами.
    Пользователь видит только свои теги + стандартные.
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(Q(owner=user) | Q(tag_type='standard'))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, tag_type='custom')


class MoodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet только для чтения настроений.
    Настроения предопределены и доступны всем.
    """
    queryset = Mood.objects.all()
    serializer_class = MoodSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с напоминаниями.
    """
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Reminder.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Отметить напоминание как выполненное"""
        reminder = self.get_object()
        reminder.status = 'completed'
        reminder.completed_at = datetime.now()
        reminder.save()
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)


# HTML Views
@method_decorator(login_required, name='dispatch')
class EntryListView(ListView):
    """Представление для списка записей (HTML)"""
    model = Entry
    template_name = 'diary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user).order_by('-entry_date')


@method_decorator(login_required, name='dispatch')
class CalendarView(TemplateView):
    """Представление календаря"""
    template_name = 'diary/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем год и месяц из параметров или используем текущие
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))

        # Создаем календарь
        cal = calendar.monthcalendar(year, month)

        # Получаем дни с записями
        entries_dates = Entry.objects.filter(
            owner=self.request.user,
            entry_date__year=year,
            entry_date__month=month
        ).values_list('entry_date', flat=True)

        entries_dates = [date.day for date in entries_dates]

        context.update({
            'calendar': cal,
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'entries_dates': entries_dates,
            'prev_month': (year, month - 1) if month > 1 else (year - 1, 12),
            'next_month': (year, month + 1) if month < 12 else (year + 1, 1),
        })

        return context


@method_decorator(login_required, name='dispatch')
class StatisticsView(APIView):
    """API для статистики"""

    def get(self, request):
        user = request.user

        # Базовая статистика
        total_entries = Entry.objects.filter(owner=user).count()
        total_words = Entry.objects.filter(owner=user).aggregate(
            total=Avg('word_count')
        )['total'] or 0

        # Статистика по настроениям
        mood_stats = Entry.objects.filter(owner=user).exclude(mood__isnull=True) \
            .values('mood__name', 'mood__emoji') \
            .annotate(count=Count('id')) \
            .order_by('-count')

        # Статистика по тегам
        tag_stats = Entry.objects.filter(owner=user) \
                        .values('tags__name', 'tags__color') \
                        .annotate(count=Count('id')) \
                        .order_by('-count')[:10]

        # Активность по месяцам
        monthly_stats = Entry.objects.filter(owner=user) \
            .extra({'month': "date_trunc('month', entry_date)"}) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        return Response({
            'total_entries': total_entries,
            'avg_words_per_entry': round(total_words, 1),
            'mood_stats': list(mood_stats),
            'tag_stats': list(tag_stats),
            'monthly_activity': list(monthly_stats),
        })


# HTML представления
class DiaryHomeView(TemplateView):
    template_name = 'diary/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Здесь будет реальная статистика из ваших моделей
        data = {
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            },
            'stats': {
                'total_entries': 156,
                'monthly_entries': 12,
                'today_entries': 1
            },
            'recent_entries': [
                {'title': 'Запись от 10 января', 'preview': 'Краткое описание записи...'},
                {'title': 'Запись от 9 января', 'preview': 'Еще одно описание...'},
                {'title': 'Запись от 8 января', 'preview': 'Последняя запись...'}
            ]
        }

        return Response(data)


# API Views
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Генерируем токены
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Генерируем токены
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Успешный вход',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Профиль успешно обновлен',
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(SimpleTokenRefreshView):
    permission_classes = [permissions.AllowAny]


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        try:
            return JsonResponse({'message': 'Успешный выход'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)


# HTML Views
class RegistrationPageView(View):
    def get(self, request):
        return render(request, 'diary/register.html')


class LoginPageView(View):
    def get(self, request):
        return render(request, 'diary/login.html')


class ProfilePageView(View):
    def get(self, request):
        return render(request, 'diary/profile.html')


class LogoutPageView(View):
    def get(self, request):
        return render(request, 'diary/logout.html')


class SettingsPageView(View):
    def get(self, request):
        return render(request, 'diary/settings.html')