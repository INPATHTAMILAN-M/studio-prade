from rest_framework import serializers
from ..models import (
    Post, Post_Link, Post_Photo, 
    Post_Video,Bookmark,Report_Post,
    Post_Link, Post_Video, Post_Photo,
    Post_Category,Brand
)

#Serializer for representing photos attached to a post.
class PostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_Photo
        fields = '__all__'

#Serializer for representing videos attached to a post.
class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_Video
        fields = '__all__'

#Serializer for representing links attached to a post.
class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_Link
        fields = ['get_current_details',]

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


#Serializer for reporting a post.
class ReportPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report_Post
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
        model = Post_Link
        fields = ['link']

#Serializer for representing videos attached to a post.
class CreatePostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_Video
        fields = ['video']

#Serializer for representing photos attached to a post.
class CreatePostPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_Photo
        fields = ['photo']

#serializer for creating a new post.
class PostCreateSerializer1(serializers.ModelSerializer):
    post_photos = CreatePostPhotoSerializer(many=True, required=False)
    post_links = CreatePostLinkSerializer(many=True, required=False)
    post_videos = CreatePostVideoSerializer(many=True, required=False)
   
    class Meta:
        model = Post
        fields = ['brand','caption','category','post_photos','post_links','post_videos']