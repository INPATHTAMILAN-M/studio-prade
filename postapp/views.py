from django.db.models import Count, Case, When, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .filters import PostFilter, BookmarkFilter
from .models import Post, Bookmark, Following, Brand
from .pagination import CustomPagination
from .serializers import * 
from .permissions.custom_permission import IsAuthenticatedForGET



class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(active=True)
    serializer_class = PostSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    permission_classes = [IsAuthenticatedForGET]
    http_method_names = ['get', 'post', 'delete', 'patch']


    def get_queryset(self):
        return super().get_queryset().filter(posted_by=self.request.user) if self.request.method != "GET" else super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = PostSerializer(data=data)

        if serializer.is_valid():
            serializer.save(posted_by=request.user)  # Save with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        # Deleting related objects manually, can be handled by cascade delete as well.
        instance.post_photos.all().delete()
        instance.post_videos.all().delete()
        instance.post_links.all().delete()
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=kwargs['pk'], posted_by=request.user)
        serializer = PostUpdateSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Save the partial update
            return Response({"message": "Post status updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkAddSerializer
    filterset_class = BookmarkFilter
    permission_classes = [IsAuthenticated] 
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        bookmarks = self.get_queryset()
        serializer = BookmarkGetSerializer(bookmarks, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    def partial_update(self, request, *args, **kwargs):
        bookmark = self.get_object()
        serializer = self.get_serializer(bookmark, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Bookmark updated", "bookmark": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        bookmark = self.get_object()
        bookmark.delete()
        return Response({"message": "Bookmark Removed"}, status=status.HTTP_204_NO_CONTENT)


class ReportPostViewSet(ModelViewSet):
    queryset = ReportPost.objects.all()
    serializer_class = ReportCreateSerializer
    permission_classes = [IsAuthenticated] 
    http_method_names = ['post']

    def get_queryset(self):
        return super().get_queryset().filter(posted_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reported_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

class LikeUnlikeViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostViewSerializer 
    permission_classes = [IsAuthenticated] 
    http_method_names = ['get']

    def get_queryset(self):
        return super().get_queryset().filter(posted_by=self.request.user)
    
    def get_serializer_class(self):
        return self.serializer_class

    def retrieve(self, request, post_id=None, *args, **kwargs):
        post = self.get_object()
        data = dict()
        post_like_unlike = Post.like_or_unlike(id=post_id, user=request.user)
        likes_count = post.likes.count()
        if post_like_unlike:
            data['liked'] = True
        data['like_count'] = likes_count

        return Response(data)    

class Suggestion(APIView):

    def get(self,request):
        get_most_followed_categories_id = set(Following.objects.filter(category__isnull=False).annotate(count=Count('category')).order_by('count').values_list('category_id', flat=True))
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(get_most_followed_categories_id)])
        categories  = PostCategory.objects.filter(id__in=get_most_followed_categories_id).order_by(preserved)[:20]

        get_most_followed_brand_ids = set(Following.objects.filter(brand__isnull=False).annotate(count=Count('brand')).order_by('count').values_list('brand_id', flat=True))
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(get_most_followed_categories_id)])
        brands  = Brand.objects.filter(id__in=get_most_followed_brand_ids).order_by(preserved)[:20]

        categories = CategoryPostSerializer(categories,many=True)
        brands = BrandPostSerializer(brands,many=True)

        context = {
            "categories":categories.data,
            "brands":brands.data,
        }
        return Response(context)