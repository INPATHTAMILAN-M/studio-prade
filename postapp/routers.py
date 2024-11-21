# urls.py
from rest_framework.routers import DefaultRouter
from .views import PostViewset, BookmarkViewSet

router = DefaultRouter()
router.register(r'posts', PostViewset, basename='post')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')


