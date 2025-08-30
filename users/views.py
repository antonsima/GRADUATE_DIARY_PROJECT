from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from config import settings
from users.models import User
from users.serializers import UserSerializer


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.save()


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout view для JWT аутентификации"""
    return Response(
        {"detail": "Successfully logged out."},
        status=status.HTTP_200_OK
    )


class CustomTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test_email'] = settings.TEST_EMAIL
        context['test_password'] = settings.TEST_PASSWORD
        return context