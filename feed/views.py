from django.db.models import Q
from django.utils.translation import ugettext
from rest_framework import decorators, exceptions as drf_exceptions, generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from feed.models import Comment, Feed, FollowRss, Rss
from feed.serializers import CommentSerializer, FeedSerializers, FeedListSerializer, RssSerializers
from utils import exceptions, responses, permissions, utils
from utils.tools import create, delete, update, retrieve


# Rss
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class RssCreateView(create.CreateView):
    """
    post:

        title min 3, max 50

        link min 5, max 100

        example

            title   zoomit

            link    https://www.zoomit.ir/feed/
    """
    serializer_class = RssSerializers
    model = Rss


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RssListView(generics.ListAPIView):
    """
    get:

        Get list of available rss

        pagination with index and size

        /?index=0&size=20

        filter

            title

            for staffs

                is_active  bool true or false blank for all
    """
    serializer_class = RssSerializers
    model = Rss

    def get(self, request):
        try:
            index, size, args = utils.pagination_util(request)
            filters = {}
            if args.get('title'):
                filters['title__icontains'] = args['title']
            if args.get('is_active') and request.user.is_staff:
                if args['is_active'].upper() == 'TRUE':
                    filters['is_active'] = True
                elif args['is_active'].upper() == 'FALSE':
                    filters['is_active'] = False

            rss_list = self.model.objects.filter(**filters)
            total = rss_list.count()
            data = self.get_serializer(rss_list[index:size], many=True).data
            return responses.SuccessResponse(data, index=index, total=total).send()
        except (exceptions.CustomException, drf_exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class RssUpdateView(update.UpdateView):
    serializer_class = RssSerializers
    model = Rss


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RsSFollowedListView(generics.ListAPIView):
    """
    get:

        Get my list of followed rss

        pagination with index and size

        /?index=0&size=20

        filter

            title

    """
    serializer_class = RssSerializers
    model = Rss

    def get(self, request):
        try:
            index, size, args = utils.pagination_util(request)
            filters = {
                'followers': request.user
            }
            if args.get('title'):
                filters['title__icontains'] = args['title']
            rss_list = self.model.objects.filter(**filters)
            total = rss_list.count()
            data = self.get_serializer(rss_list[index:size], many=True).data
            return responses.SuccessResponse(data, index=index, total=total).send()
        except (exceptions.CustomException, drf_exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RssFollowView(generics.GenericAPIView):
    serializer_class = serializers.Serializer
    model = Rss

    def post(self, request, id):
        try:
            rss = self.model.objects.get(id=id, is_active=True)
            rss.followers.add(request.user)
            return responses.SuccessResponse(status=200).send()
        except (exceptions.CustomException, self.model.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()

    def delete(self, request, id):
        try:
            rss = self.model.objects.get(id=id, is_active=True)
            rss.followers.remove(request.user)
            return responses.SuccessResponse(status=204).send()
        except (exceptions.CustomException, self.model.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


# Feed
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class FeedListView(generics.ListAPIView):
    """
    get:

        Get list of all feeds

        pagination with index and size

        /?index=0&size=20

        filter

            search  search on title and description

        order_by

            OLDEST

            NEWEST default

    """
    serializer_class = FeedSerializers
    model = Feed

    def get(self, request):
        try:
            index, size, args = utils.pagination_util(request)

            feed_list = self.model.objects.filter()
            if args.get('search'):
                feed_list = feed_list.filter(Q(title__icontains=args['search']) |
                                             Q(description__icontains=args['search'])).distinct()
            if args.get('order_by') and args['order_by'] == 'OLDEST':
                feed_list = feed_list.order_by('published')
            total = feed_list.count()
            data = self.get_serializer(feed_list[index:size], many=True).data
            return responses.SuccessResponse(data, index=index, total=total).send()
        except (exceptions.CustomException, drf_exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RssFeedUnreadView(generics.ListAPIView):
    """
    get:

        Get unread feeds on this rss if followed by user

    """
    serializer_class = serializers.Serializer
    model = Rss

    def get(self, request, id):
        try:
            rss = self.model.objects.get(id=id, is_active=True)
            fs = FollowRss.objects.filter(rss=rss, user=request.user)
            if fs:
                count = Feed.objects.filter(rss=rss, published__gte=fs[0].last_seen).count()
                data = {
                    'unread': count if count else 0
                }
                return responses.SuccessResponse(data).send()
            else:
                raise exceptions.CustomException(detail=ugettext('You did not follow this Rss.'))
        except (exceptions.CustomException, drf_exceptions.ValidationError, Rss.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class RssFeedListView(generics.ListAPIView):
    """
    get:

        Get list of available feeds of rss

        pagination with index and size

        /?index=0&size=20

        filter

            title

        order_by

            OLDEST

            NEWEST default

    """
    serializer_class = FeedListSerializer
    model = Feed

    def get(self, request, id):
        try:
            index, size, args = utils.pagination_util(request)
            rss = Rss.objects.get(id=id, is_active=True)
            # Update last seen this rss
            FollowRss.objects.filter(rss=rss, user=request.user).update(last_seen=utils.now_time())
            filters = {
                'rss': rss
            }
            if args.get('title'):
                filters['title__icontains'] = args['title']

            feed_list = self.model.objects.filter(**filters)
            if args.get('order_by') and args['order_by'] == 'OLDEST':
                feed_list = feed_list.order_by('published')
            total = feed_list.count()
            data = self.get_serializer(feed_list[index:size], many=True).data
            return responses.SuccessResponse(data, index=index, total=total).send()
        except (exceptions.CustomException, drf_exceptions.ValidationError, Rss.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated, permissions.SuperUserPermission])
class FeedDeleteView(delete.DeleteView):
    serializer_class = FeedSerializers
    model = Feed


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class FeedRetrieveView(retrieve.RetrieveView):
    serializer_class = FeedSerializers
    model = Feed


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class FeedFavoriteView(generics.GenericAPIView):
    serializer_class = serializers.Serializer
    model = Feed

    def post(self, request, id):
        try:
            feed = self.model.objects.get(id=id, is_deleted=False)
            feed.favorites.add(request.user)
            return responses.SuccessResponse(status=201).send()
        except (exceptions.CustomException, self.model.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()

    def delete(self, request, id):
        try:
            feed = self.model.objects.get(id=id, is_deleted=False)
            feed.favorites.remove(request.user)
            return responses.SuccessResponse(status=204).send()
        except (exceptions.CustomException, self.model.DoesNotExist) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class FeedListOfMyFavoritesView(generics.ListAPIView):
    """
    get:

        Get list of my favorite feeds

        pagination with index and size

        /?index=0&size=20

        filter

            search  search on title and description

    """
    serializer_class = FeedSerializers
    model = Feed

    def get(self, request):
        try:
            index, size, args = utils.pagination_util(request)
            filters = {
                'favorites': request.user
            }
            feed_list = self.model.objects.filter(**filters)
            if args.get('search'):
                feed_list = feed_list.filter(Q(title__icontains=args['search']) |
                                           Q(description__icontains=args['search'])).distinct()
            if args.get('order_by') and args['order_by'] == 'OLDEST':
                feed_list = feed_list.order_by('published')
            total = feed_list.count()
            data = self.get_serializer(feed_list[index:size], many=True).data
            return responses.SuccessResponse(data, index=index, total=total).send()
        except (exceptions.CustomException, drf_exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()


# Comment
@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CommentCreateView(create.CreateView):
    """
    post:

        create comment on feed

            body min 2, max 500

            feed  {'id': id of feed}
    """
    serializer_class = CommentSerializer
    model = Comment


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CommentView(delete.DeleteView, update.UpdateView):
    """
    delete:

        delete comment by creator of comment or superuser permission

    put:

         update comment by creator

    """
    serializer_class = CommentSerializer
    model = Comment


@decorators.authentication_classes([JSONWebTokenAuthentication])
@decorators.permission_classes([IsAuthenticated])
class CommentListFeedView(generics.ListAPIView):
    """
    get:

        Get list of my favorite feeds

        pagination with index and size

        /?index=0&size=20

        order_by

            OLDEST

            NEWEST default

    """
    serializer_class = CommentSerializer
    model = Comment

    def get(self, request, id):
        try:
            index, size, args = utils.pagination_util(request)
            comment_list = Comment.objects.filter(feed__id=id, feed__is_deleted=False, is_deleted=False)
            if args.get('order_by') and args['order_by'] == 'OLDEST':
                comment_list = comment_list.order_by('created')
            total = comment_list.count()
            data = self.get_serializer(comment_list[index:size], many=True).data
            return responses.SuccessResponse(data, index=index, total=total).send()
        except (exceptions.CustomException, drf_exceptions.ValidationError) as e:
            return responses.ErrorResponse(message=e.detail, status=e.status_code).send()
