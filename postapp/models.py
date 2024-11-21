from django.db import models
from account.models import User
import requests


# Report and Bookmark Models
class ReportPost(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE,related_name="report_post")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    message  = models.TextField()

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

# Following Models
class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE,null=True,blank=True)
    category = models.ForeignKey('PostCategory',on_delete=models.CASCADE,null=True,blank=True)
    following_user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name="following_user")

    def __str__(self):
        return str(self.brand) 


# Category Models
class PostCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

    @property
    def post_count(self):
        return self.post_set.filter(active=True).count()
    @property
    def followers_count(self):
        return Following.objects.filter(category=self).count()  
    @property
    def posts(self):
        return Post.objects.filter(category=self)


class Brand(models.Model):
    name = models.CharField(max_length=200)
    display_picture = models.ImageField(upload_to="brand",blank=True)

    def __str__(self):
        return self.name

    @property
    def post_count(self):
        return self.post_set.filter(active=True).count()
    
    @property
    def followers_count(self):
        return Following.objects.filter(brand=self).count()  
    
    @property
    def posts(self):
        return Post.objects.filter(brand=self)


# Post Models    
class Post(models.Model):
    category = models.ForeignKey(PostCategory,on_delete=models.CASCADE)
    caption  = models.TextField()
    posted_by =  models.ForeignKey(User, on_delete=models.CASCADE,related_name="posted_by")
    likes = models.ManyToManyField(User)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now=True,null=True)
    active  = models.BooleanField(default=True)

    @property
    def get_likes_count(self):
        return self.likes.all().count()

    def like_or_unlike(id,user):
        if Post.objects.filter(id=id,likes=user).exists():
            post = Post.objects.get(id=id)
            post.likes.remove(user)
            return False
        else:
            post = Post.objects.get(id=id)
            post.likes.add(user)
            return True

class PostLink(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_links")
    link = models.URLField(max_length=250)
    slug = models.SlugField(max_length=255,null=True,blank=True)

    @property
    def get_current_details(self):
        print(self.slug)  

        r = requests.get('https://suvado.in/rdbs/wp-json/wc/v3/products?slug='+self.slug+'&consumer_key=ck_6613f2980d3115e64ad4f0a75778a266c781bdd6&consumer_secret=cs_35232f784da90c5508abc2cd2e9a9180ba4a54c6')
        print(r.json())
        print(r.status())
      
        return self.slug

class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_photos")
    photo = models.ImageField(upload_to='postphotos')

class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_videos")
    video = models.FileField(upload_to='postvideos')

