from rest_framework import serializers
from .models import User
from account.models import User
from postapp.models import Following, Brand, Post, PostCategory

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


#Serializer for the user's profile details
class My_Profile_Serializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['first_name','last_name','email','profile_picture']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

#Serializer for updating the user profile details.
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']  

    def get_followers_count(self, obj):
        return Following.objects.filter(following_user=obj).count()
    

class Password_Reset_Serializer(serializers.Serializer):
    email = serializers.EmailField()


class FollowingSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=PostCategory.objects.all(), required=False)
    following_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Following
        fields = ['brand', 'category', 'following_user']

    def validate(self, data):
        # Custom validation to ensure only one of brand, category, or following_user is provided
        if not any([data.get('brand'), data.get('category'), data.get('following_user')]):
            raise serializers.ValidationError("At least one of brand, category, or following_user must be provided.")
        
        # Ensure that the user cannot follow themselves
        if data.get('following_user') == self.context['request'].user:
            raise serializers.ValidationError("You cannot follow yourself.")

        return data
    
