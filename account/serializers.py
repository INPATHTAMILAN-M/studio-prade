from rest_framework import serializers
from .models import User
from postapp.models import Following
from account.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

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

#Serializer for Reset the user's password.
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def send_reset_email(self, user, token):
        subject = 'Password Reset'
        message = render_to_string(
            'password_reset_email.html',
            {
                'user': user,
                'token': token,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            },
        )
        email = EmailMessage(subject, message, to=[user.email])
        email.send()

    def reset_password(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
       
        token = default_token_generator.make_token(user)
        self.send_reset_email(user, token)
        return user


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

#Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

#Serializer for changing the user's password.
class ChangePassword_Serializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

#Serializer for representing followed brands    
class Following_Serializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    class Meta:
        model = Following
        fields = ['brand_name']   

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



