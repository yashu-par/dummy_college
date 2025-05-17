from django.db import models
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserRegistrationManager(models.Manager):
    def create_user(self, username, email, password, mobile=None, role='user'):
        if not username or not email or not password:
            raise ValueError('Username, email and password are required')
        
        user = self.model(
            username=username,
            email=email,
            password=make_password(password),
            mobile=mobile,
            role=role
        )
        user.save(using=self._db)
        return user

class UserRegistration(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Password ko encrypted rakhna better hai (abhi plain for simplicity)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default='user')

    objects = UserRegistrationManager()

    def __str__(self):
        return self.username
    
    #for edit profile
   

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_registration = models.OneToOneField(UserRegistration, on_delete=models.CASCADE, null=True)
    bio = models.TextField(blank=True)
    about = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    education = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=50, default='user')
    title = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # If user_registration is not set, try to find it
        if not self.user_registration:
            try:
                self.user_registration = UserRegistration.objects.get(username=self.user.username)
            except UserRegistration.DoesNotExist:
                pass
        super().save(*args, **kwargs)

#create post


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True)
    private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:30]
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

class PostShare(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shared_by.username} shared post {self.post.id if self.post else 'None'}"

#message


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:20]}"

#user_profile
#connect user_profile to user_registration


class ConnectionRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')

    def __str__(self):
        return f"{self.from_user} to {self.to_user} ({self.status})"
