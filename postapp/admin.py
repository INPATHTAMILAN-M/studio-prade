from django.contrib import admin
from .models import *

# Register your models here.

class Post_Category_Admin(admin.ModelAdmin):
        pass

class Post_Link_Admin(admin.ModelAdmin):
        list_display = ['post','link','get_current_details']

class Brand_Admin(admin.ModelAdmin):
        pass

class Post_Link_Inline(admin.TabularInline):
    model = PostLink


class Post_Photo_Inline(admin.TabularInline):
    model = PostPhoto

class Post_Video_Inline(admin.TabularInline):
    model = PostVideo

class Post_Admin(admin.ModelAdmin):
    list_display = ['posted_by','caption','get_likes_count']
    list_filter = ['posted_by','category','brand','posted_on']
    inlines = [Post_Link_Inline,Post_Video_Inline,Post_Photo_Inline ]


class Bookmark_Admin(admin.ModelAdmin):
    list_filter = ['user','post__category','post__brand','user']


class Post_Photo_Admin(admin.ModelAdmin):
        pass

class Post_Video_Admin(admin.ModelAdmin):
        pass

class Report_Post_Admin(admin.ModelAdmin):
        pass

class Following_Admin(admin.ModelAdmin):
    list_display = ['user','category','brand','following_user']

admin.site.register(PostCategory,Post_Category_Admin)
admin.site.register(Brand,Brand_Admin)
admin.site.register(Post,Post_Admin)
admin.site.register(PostLink,Post_Link_Admin)
admin.site.register(PostPhoto,Post_Photo_Admin)
admin.site.register(PostVideo,Post_Video_Admin)
admin.site.register(Bookmark,Bookmark_Admin)
admin.site.register(ReportPost,Report_Post_Admin)
admin.site.register(Following,Following_Admin)



