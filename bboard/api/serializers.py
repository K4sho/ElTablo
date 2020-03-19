from rest_framework import serializers

from main.models import Bb, Comment


class BbSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка последних 10 объявлений"""
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at')


class BbDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для получения сведений о конкретном объявлении"""
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at', 'contacts', 'image')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для отправки списка комментариев и добавления нового"""
    class Meta:
        model = Comment
        fields = ('bb', 'author', 'content', 'created_at')