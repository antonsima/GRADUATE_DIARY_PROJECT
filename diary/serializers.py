from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from .models import Entry, Tag, Mood, Reminder
from markdownx.utils import markdownify

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color', 'tag_type', 'created_at']


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['id', 'name', 'emoji', 'level', 'description']


class EntrySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    mood = MoodSerializer(read_only=True)
    mood_id = serializers.PrimaryKeyRelatedField(
        queryset=Mood.objects.all(),
        source='mood',
        write_only=True,
        required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    word_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = Entry
        fields = [
            'id', 'title', 'content', 'content_html', 'date_created', 'date_updated',
            'entry_date', 'is_public', 'mood', 'mood_id', 'tags', 'tag_ids',
            'owner', 'word_count', 'reading_time'
        ]
        read_only_fields = ['owner', 'content_html', 'date_created', 'date_updated']


class EntryDetailSerializer(EntrySerializer):
    """Сериализатор с дополнительными данными для детального просмотра"""

    class Meta(EntrySerializer.Meta):
        fields = EntrySerializer.Meta.fields + ['content_html']


class ReminderSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Reminder
        fields = [
            'id', 'title', 'description', 'due_date', 'priority', 'status',
            'tags', 'tag_ids', 'created_at', 'completed_at', 'is_overdue'
        ]
        read_only_fields = ['owner', 'created_at', 'completed_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                raise serializers.ValidationError('Неверные учетные данные')

            if not user.is_active:
                raise serializers.ValidationError('Аккаунт отключен')

            attrs['user'] = user
            return attrs

        raise serializers.ValidationError('Email и пароль обязательны')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('email', 'date_joined')


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password or password2:
            if password != password2:
                raise serializers.ValidationError({"password": "Пароли не совпадают"})
            if password:
                try:
                    validate_password(password)
                except ValidationError as e:
                    raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password2', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance