from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, Case, When, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from account.models import User
from account.serializers import My_Profile_Serializer
from .models import Post, Bookmark, PostPhoto, PostVideo, PostLink, Following, Brand
from .serializers import *
from .filters import PostFilter, BookmarkFilter


class CustomPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'   
    page_query_param = 'page'
    
class PostViewset(ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    queryset = Post.objects.filter(active=True)
    serializer_class = PostSerializer
    def create(self, request, *args, **kwargs):
        data = request.data
        photos = request.FILES.getlist('post_photos')
        links = data.get('post_links', [])
        videos = request.FILES.getlist('post_videos')

        serializer = PostCreateSerializer1(data=data)
        if serializer.is_valid():
            post = serializer.save(posted_by=request.user)

            # Save related photos, links, and videos
            for photo in photos:
                PostPhoto.objects.create(post=post, photo=photo)
            for link in links:
                PostLink.objects.create(post=post, link=link)
            for video in videos:
                PostVideo.objects.create(post=post, video=video)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(id=kwargs['pk'], posted_by=request.user)
            post.delete()
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(id=kwargs['pk'], posted_by=request.user)
            active = request.data.get('active')
            if active is not None:
                post.active = active
                post.save()
                return Response({"message": "Post status updated."}, status=status.HTTP_200_OK)
            return Response({"error": "Active field is required."}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)


class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkAddSerializer
    filterset_class = BookmarkFilter


    def get_queryset(self):
        return Bookmark.objects.all()
    
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


class ReportView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReportPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reported_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class LikeUnlikeView(APIView):
    def get(self,request,pk):
        data =  dict()    
        post_like_unlike = Post.like_or_unlike(id=pk,user=request.user)
        post = Post.objects.get(id=pk)
        likes_count = post.likes.count()
        if post_like_unlike:    
            data['liked'] = True
            data['like_count'] = likes_count
        else:
            data['like_count'] = likes_count
            
        return Response(data)



class PostFilter(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        hashtag = request.data.get('hashtag', '')
        brand = request.data.get('brand', '')
        category = request.data.get('category', '')

        if not hashtag and not brand and not category:
            return Response({"message": "Please provide a hashtag, brand name, or category."}, status=400)

        filtered_posts = Post.objects.all()

        if hashtag:
            filtered_posts = filtered_posts.filter(Q(caption__icontains=f"#{hashtag}"))

        if brand:
            filtered_posts = filtered_posts.filter(brand__name__icontains=brand)
        
        if category:
            filtered_posts = filtered_posts.filter(category__name__icontains=category)

        if not filtered_posts.exists():
            return Response({"message": "No posts found with the given criteria."}, status=404)
    
        serializer = PostViewSerializer(filtered_posts, many=True)
        return Response(serializer.data)


class FollowingPostFilter(APIView):
    def get(self, request, *args, **kwargs):  
        following_users = Following.objects.filter(user= request.user).values_list('following_user', flat=True)
        following_brands = Following.objects.filter(user= request.user, brand__isnull=False).values_list('brand', flat=True)
        following_categories = Following.objects.filter(user= request.user, category__isnull=False).values_list('category', flat=True)

        posts = Post.objects.filter(Q(posted_by__in=following_users)|Q(brand__in=following_brands)|Q(category__in=following_categories))

        serializer = PostViewSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Suggestion(APIView):
    authentication_classes = ()
    permission_classes = ()

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