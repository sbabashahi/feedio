from django.urls import path

from feed import views as feed_views


urlpatterns = [
    # rss
    path('rss/rss/', feed_views.RssCreateView.as_view()),
    path('rss/rss_list/', feed_views.RssListView.as_view()),
    path('rss/followed_rss/', feed_views.RssFollowedListView.as_view()),
    path('rss/rss/<int:id>/', feed_views.RssUpdateView.as_view()),
    path('rss/follow_rss/<int:id>/', feed_views.RssFollowView.as_view()),
    # feed
    path('feed/feed_list/', feed_views.FeedListView.as_view()),
    path('feed/favorite_feed/', feed_views.FeedListOfMyFavoritesView.as_view()),
    path('feed/rss_unread_feed/<int:id>/', feed_views.RssFeedUnreadView.as_view()),
    path('feed/rss_feed/<int:id>/', feed_views.RssFeedListView.as_view()),
    path('feed/feed/<int:id>/', feed_views.FeedDeleteRetrieveView.as_view()),
    path('feed/favorite_feed/<int:id>/', feed_views.FeedFavoriteView.as_view()),
    path('feed/comment_list/<int:id>/', feed_views.CommentListFeedView.as_view()),
    # comment
    path('comment/comment/', feed_views.CommentCreateView.as_view()),
    path('comment/comment/<int:id>/', feed_views.CommentView.as_view()),
]

