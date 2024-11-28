from rest_framework import serializers
from .models import User
from account.models import User


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
class Edit_Profile_Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['first_name','last_name','email','profile_picture']    

class Password_Reset_Serializer(serializers.Serializer):
    email = serializers.EmailField()



