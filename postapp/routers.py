# urls.py
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, BookmarkViewSet, LikeUnlikeViewSet, ReportPostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'post-like', LikeUnlikeViewSet, basename='post_view')
router.register(r'report-post', ReportPostViewSet, basename='report_post')

