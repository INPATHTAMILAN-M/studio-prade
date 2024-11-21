from rest_framework import serializers
from .models import *


#Serializer for representing photos attached to a post.
class PostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPhoto
        fields = '__all__'

#Serializer for representing videos attached to a post.
class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = '__all__'

#Serializer for representing links attached to a post.
class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLink
        fields = ['get_current_details',]

#Serializer for post.
class PostSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    posted_by = serializers.StringRelatedField()
    post_photos  = PostPhotoSerializer(many=True, read_only=True)
    post_videos  = PostVideoSerializer(many=True, read_only=True)
    post_links  = PostLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'category', 'caption','posted_by','brand','posted_on','post_photos','post_videos','post_links')

#Serializer for bookmarked posts.
class BookmarkGetSerializer(serializers.ModelSerializer):
    post_category = serializers.CharField(source='post.category.name', read_only=True)
    post_name = serializers.CharField(source='post.category.name', read_only=True)
    post_caption = serializers.CharField(source='post.caption', read_only=True)
    post_likes_count = serializers.IntegerField(source='post.likes.count', read_only=True)
    post_brand = serializers.CharField(source='post.brand.name', read_only=True)
    post_posted_on = serializers.DateTimeField(source='post.posted_on', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['post_id','post_category','post_name','post_caption','post_likes_count','post_brand', 'post_posted_on']

    def get_post_likes_count(self, obj):
        return obj.post.get_likes_count()

#Serializer for adding a bookmark to a post.
class BookmarkAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'

#Serializer for reporting a post.
class ReportPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPost
        fields = ['post','message']

#Serializer for representing post details.
class PostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

#Serializer for creating a new post.
class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['brand','caption','category']

#Serializer for representing links attached to a post.
class CreatePostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLink
        fields = ['link']

#Serializer for representing videos attached to a post.
class CreatePostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ['video']

#Serializer for representing photos attached to a post.
class CreatePostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPhoto
        fields = ['photo']

#serializer for creating a new post.
class PostCreateSerializer1(serializers.ModelSerializer):
    post_photos = CreatePostPhotoSerializer(many=True, required=False)
    post_links = CreatePostLinkSerializer(many=True, required=False)
    post_videos = CreatePostVideoSerializer(many=True, required=False)
   
    class Meta:
        model = Post
        fields = ['brand','caption','category','post_photos','post_links','post_videos']

#Serializes post category including its id,name,post count,followers count and post
class CategoryPostSerializer(serializers.ModelSerializer):
    #posts = serializers.SerializerMethodField()
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = PostCategory
        fields = ['id','name','post_count','followers_count','posts']

#Serializes post brand including its id,name,post count,followers count and post
class BrandPostSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Brand
        fields = ['id','name','post_count','followers_count','posts']