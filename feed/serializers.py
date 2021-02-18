from django.db import transaction
from django.utils.translation import ugettext
from rest_framework import serializers

from feed.models import Comment, Feed, Rss
from utils import exceptions, tasks


class RssSerializers(serializers.Serializer):
    id = serializers.ReadOnlyField()
    title = serializers.CharField(max_length=50, min_length=3, required=True)
    link = serializers.CharField(max_length=100, min_length=5, required=True)
    is_active = serializers.BooleanField(default=True)

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        if not self.context['request'].user.is_staff:
            instance.pop('is_active')
        return instance

    @transaction.atomic
    def create(self, validated_data):
        rss = Rss(**validated_data)
        rss.save()
        tasks.check_new_rss.apply_async(args=(rss.id,), retry=False)
        return rss

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = Rss.objects.select_for_update().get(id=instance.id)
        if validated_data.get('title') and instance.title != validated_data['title']:
            instance.title = validated_data['title']

        if validated_data.get('link') and instance.link != validated_data['link']:
            instance.link = validated_data['link']

        if validated_data.get('is_active') and instance.is_active != validated_data['is_active']:
            instance.is_active = validated_data['is_active']

        instance.save()
        return instance


class NestedRssSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.ReadOnlyField()


class FeedSerializers(serializers.Serializer):
    id = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    link = serializers.ReadOnlyField()
    published = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    rss = NestedRssSerializer(read_only=True)
    is_deleted = serializers.ReadOnlyField()

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        if not self.context['request'].user.is_staff:
            instance.pop('is_deleted')
        return instance


class FeedListSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    description = serializers.ReadOnlyField()
    rss = NestedRssSerializer(read_only=True)


class NestedFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class CommentSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    body = serializers.CharField(max_length=500, min_length=2)
    feed = NestedFeedSerializer(write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data['feed'] = Feed.objects.get(id=validated_data['feed']['id'], is_deleted=False)
        except Rss.DoesNotExist as e:
            raise exceptions.CustomException(detail=ugettext('Feed does not exist.'))
        validated_data['user'] = self.context['request'].user
        comment = Comment(**validated_data)
        comment.save()
        return comment

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = Comment.objects.select_for_update().get(id=instance.id)
        if validated_data.get('body') and instance.body != validated_data['body']:
            instance.body = validated_data['body']
        instance.save()
        return instance
