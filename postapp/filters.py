
import django_filters
from .models import Post, Bookmark

class PostFilter(django_filters.FilterSet):
    
    class Meta:
        model = Post
        fields = "__all__"

class BookmarkFilter(django_filters.FilterSet):
    class Meta:
        model = Bookmark
        fields = "__all__"


