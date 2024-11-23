
import django_filters
from django.db.models import Q
from .models import Post, Bookmark,Following



class PostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    caption  = django_filters.CharFilter(field_name='caption', lookup_expr='icontains')
    posted_by =  django_filters.CharFilter(field_name='posted_by', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='brand__name', lookup_expr='icontains')
    posted_on = django_filters.DateFilter(field_name='posted_on', lookup_expr='icontains')
    active  = django_filters.BooleanFilter(field_name='active', lookup_expr='exact')
    hashtags = django_filters.CharFilter(method='filter_hashtags')
    following = django_filters.BooleanFilter(method='filter_by_following', label="Filter by Following")

    class Meta:
        model = Post
        fields = "__all__"

    def filter_hashtags(self, queryset, name, value):
        """
        Custom filter method for filtering posts containing hashtags.
        """
        return queryset.filter(caption__icontains=f"#{value}")

    def filter_by_following(self, queryset, name, value):
        """
        Custom filtering logic to filter posts based on user followings.
        """
        user = value  # The current user passed to the filter
        if not user.is_authenticated:
            return queryset.none()  # Return no posts if the user is not authenticated

        # Fetch following data
        following_users = Following.objects.filter(user=user).values_list('following_user', flat=True)
        following_brands = Following.objects.filter(user=user, brand__isnull=False).values_list('brand', flat=True)
        following_categories = Following.objects.filter(user=user, category__isnull=False).values_list('category', flat=True)

        # Filter posts based on followings
        return queryset.filter(
            Q(posted_by__in=following_users) |
            Q(brand__in=following_brands) |
            Q(category__in=following_categories)
        )

class BookmarkFilter(django_filters.FilterSet):
    class Meta:
        model = Bookmark
        fields = "__all__"


