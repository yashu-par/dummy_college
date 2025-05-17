from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json
import random
from .models import UserRegistration, UserProfile, Post
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.core.serializers import serialize
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from .models import Post, Like, Comment
from .models import Post, PostShare
from django.shortcuts import render, redirect, get_object_or_404
from .models import ConnectionRequest

# import re
# from django.utils.timesince import timesince
# from django.contrib import messages
# from django.core.paginator import Paginator
# from django.db.models import Q

# from django.contrib.auth import authenticate, login
# from django.utils import timezone
# from .models import Job
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Conversation, Message
# from django.contrib.auth.models import User
# from rest_framework.decorators import api_view
# from django.contrib.auth import get_user_model
# from rest_framework.permissions import AllowAny
# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from django.conf import settings
# from .models import EmailOTP
# import random
# from django.core.mail import get_connection, EmailMessage
# import ssl
# from django.core.mail import send_mail
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required

# Create your views here.

def indexpage(request):
   template = loader.get_template('index.html')
   return HttpResponse(template.render())

def loginpage(request):
  template = loader.get_template('login.html')
  return HttpResponse(template.render())

def signuppage(request):
   template = loader.get_template('signup.html')
   return HttpResponse(template.render())

def contactpage(request):
   template = loader.get_template('contact.html')
   return HttpResponse(template.render())

def Updatepage(request):
   template = loader.get_template('Update.html')
   return HttpResponse(template.render())

def Deletepage(request):
   template = loader.get_template('Delete.html')
   return HttpResponse(template.render())

@login_required
def profilepage(request):
    # Get all users except the current user
    all_users = User.objects.exclude(id=request.user.id)
    
    # Get pending connection requests for the current user
    received_requests = ConnectionRequest.objects.filter(to_user=request.user, status='pending')
    
    # Get sent connection requests
    sent_requests = ConnectionRequest.objects.filter(from_user=request.user, status='pending')
    
    # Get IDs of users who have pending requests from current user
    sent_request_user_ids = sent_requests.values_list('to_user_id', flat=True)
    
    # Get existing connections (both sent and received)
    existing_connections = ConnectionRequest.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)),
        status='accepted'
    ).values_list('from_user_id', 'to_user_id')
    
    # Flatten the connections list to get all connected user IDs
    connected_user_ids = set()
    for from_id, to_id in existing_connections:
        connected_user_ids.add(from_id)
        connected_user_ids.add(to_id)
    
    template = loader.get_template('profile.html')
    context = {
        'all_users': all_users,
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'connected_user_ids': connected_user_ids,
        'sent_request_user_ids': sent_request_user_ids
    }
    return HttpResponse(template.render(context, request))

def myprofile(request):
   template = loader.get_template('myprofile.html')
   return HttpResponse(template.render())


def message(request):
   template = loader.get_template('message.html')
   return HttpResponse(template.render())


def editprofile(request):
   template = loader.get_template('editprofile.html')
   return HttpResponse(template.render())


def post(request):
   template = loader.get_template('post.html')
   return HttpResponse(template.render()) 

def createpost(request):
   template = loader.get_template('createpost.html')
   return HttpResponse(template.render())

@csrf_exempt
def signupdata(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            mobile = data.get("mobile")
            role = data.get("role", "user")

            # Validate required fields
            if not username or not email or not password:
                return JsonResponse({"error": "Username, email, and password are required"}, status=400)

            # Validate email format
            if not '@' in email or not '.' in email:
                return JsonResponse({"error": "Invalid email format"}, status=400)

            # Check if username already exists
            if UserRegistration.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)

            # Check if email already exists
            if UserRegistration.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already registered"}, status=400)

            try:
                # Create UserRegistration
                user_reg = UserRegistration.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    mobile=mobile,
                    role=role
                )

                # Create Django User
                django_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Create UserProfile and link it with both User and UserRegistration
                UserProfile.objects.create(
                    user=django_user,
                    user_registration=user_reg,
                    bio='',
                    skills='',
                    education='',
                    experience=''
                )

                return JsonResponse({
                    'message': 'User registered successfully',
                    'user': {
                        'id': user_reg.id,
                        'username': user_reg.username,
                        'email': user_reg.email,
                        'mobile': user_reg.mobile,
                        'role': user_reg.role,
                        'is_verified': user_reg.is_verified,
                    }
                }, status=201)

            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def logindata(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)

            try:
                user = UserRegistration.objects.get(username=username)
                if check_password(password, user.password):
                    # Create or get Django User
                    django_user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': user.email,
                            'is_active': True
                        }
                    )
                    
                    # Set the session
                    auth_login(request, django_user)
                    
                    return JsonResponse({
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'mobile': user.mobile,
                            'role': user.role,
                            'is_verified': user.is_verified,
                        }
                    })
                else:
                    return JsonResponse({"error": "Invalid password"}, status=400)
            except UserRegistration.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

#edit profile

@require_http_methods(["POST"])
def save_profile(request):
    try:
        data = json.loads(request.body)
        user = request.user

        # Get the UserProfile object for this user
        profile = UserProfile.objects.get(user=user)

        # Only update username if it's different and not taken
        new_username = data.get('username', user.username)
        if new_username != user.username:
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return JsonResponse({'error': 'Username already taken'}, status=400)
            user.username = new_username

        profile.bio = data.get('bio', '')
        profile.skills = data.get('skills', '')
        profile.education = data.get('education', '')
        profile.experience = data.get('experience', '')

        # Handle profile image if provided
        if data.get('profile_image'):
            # Save profile image logic here
            pass

        user.save()
        profile.save()

        return JsonResponse({
            'message': 'Profile updated successfully',
            'profile': {
                'username': user.username,
                'bio': profile.bio,
                'skills': profile.skills,
                'education': profile.education,
                'experience': profile.experience,
                'profile_image': profile.profile_image.url if profile.profile_image else None
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def get_profile_data(request):
    if request.method == "GET":
        try:
            # Get the user profile
            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                # If profile doesn't exist, create one
                user_reg = UserRegistration.objects.get(username=request.user.username)
                profile = UserProfile.objects.create(
                    user=request.user,
                    user_registration=user_reg,
                    bio='',
                    skills='',
                    education='',
                    experience=''
                )

            # Get user registration data
            user_reg = profile.user_registration

            # Prepare profile data
            profile_data = {
                'username': request.user.username,
                'email': request.user.email,
                'bio': profile.bio or 'No bio available',
                'skills': profile.skills or 'No skills listed',
                'education': profile.education or 'No education listed',
                'experience': profile.experience or 'No experience listed',
                'profile_image': profile.profile_image.url if profile.profile_image else None,
                'mobile': user_reg.mobile if user_reg else '',
                'role': user_reg.role if user_reg else 'user',
                'is_verified': user_reg.is_verified if user_reg else False
            }

            return JsonResponse({
                'profile': profile_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

#create post

@csrf_exempt
@login_required
def create_post(request):
    if request.method == "POST":
        data = request.POST
        title = data.get("title")
       # category = data.get("category")
        tags = data.get("tags")
        private = data.get("private") == "true"
        image = request.FILES.get("image")
        post = Post.objects.create(
            user=request.user,
            title=title,
            #category=category,
            tags=tags,
            private=private,
            image=image
        )
        return JsonResponse({"message": "Post created", "id": post.id})
    return JsonResponse({"error": "Invalid method"}, status=405)

def get_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    posts_data = []
    for post in posts:
        posts_data.append({
            "id": post.id,
            "user": post.user.username,
            "title": post.title,
            "image": post.image.url if post.image else "",
            #"category": post.category,
            "tags": post.tags,
            "private": post.private,
            "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return JsonResponse({"posts": posts_data})
#like post


@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        return JsonResponse({'status': 'unliked'})
    return JsonResponse({'status': 'liked'})

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('comment')
        Comment.objects.create(user=request.user, post_id=post_id, content=content)
        return JsonResponse({'status': 'commented'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@csrf_exempt
@login_required
def share_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = data.get("post_id")

            if not post_id:
                return JsonResponse({"status": "error", "message": "Post ID is required"}, status=400)

            post = Post.objects.get(id=post_id)

            # Optional: prevent sharing multiple times
            already_shared = PostShare.objects.filter(shared_by=request.user, post=post).exists()
            if already_shared:
                return JsonResponse({"status": "error", "message": "Already shared"}, status=400)

            PostShare.objects.create(shared_by=request.user, post=post)
            return JsonResponse({"status": "success", "message": "Post shared successfully"})

        except Post.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

# You can add a share view if you want to track sharing (e.g., copy link, send via message)



#message
#send message
@csrf_exempt
@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        receiver_id = data.get("receiver_id")
        content = data.get("content")

        try:
            receiver = User.objects.get(id=receiver_id)
            message = Message.objects.create(sender=request.user, receiver=receiver, content=content)
            return JsonResponse({
                "status": "success",
                "data": {
                    "content": message.content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M"),
                }
            })
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
#get messages


@login_required
def get_messages(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=other_user) |
            Q(sender=other_user, receiver=request.user)
        ).order_by("timestamp")

        message_list = [
            {
                "sender": msg.sender.username,
                "receiver": msg.receiver.username,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M")
            }
            for msg in messages
        ]

        return JsonResponse({"messages": message_list})
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

#connect user_profile to user_registration


@login_required
def send_connection_request(request):
    if request.method == 'POST':
        try:
            to_user_id = request.POST.get('to_user')
            to_user = User.objects.get(id=to_user_id)
            
            # Check if request already exists
            if ConnectionRequest.objects.filter(
                from_user=request.user,
                to_user=to_user,
                status='pending'
            ).exists():
                return JsonResponse({'error': 'Request already sent'}, status=400)
            
            # Check if already connected
            if ConnectionRequest.objects.filter(
                (Q(from_user=request.user, to_user=to_user) | 
                 Q(from_user=to_user, to_user=request.user)),
                status='accepted'
            ).exists():
                return JsonResponse({'error': 'Already connected'}, status=400)
            
            # Create new connection request
            ConnectionRequest.objects.create(
                from_user=request.user,
                to_user=to_user,
                status='pending'
            )
            
            return JsonResponse({'status': 'Request sent successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def accept_connection_request(request):
    if request.method == 'POST':
        try:
            request_id = request.POST.get('request_id')
            conn_request = ConnectionRequest.objects.get(
                id=request_id,
                to_user=request.user,
                status='pending'
            )
            conn_request.status = 'accepted'
            conn_request.save()
            return JsonResponse({'status': 'Request accepted'})
        except ConnectionRequest.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def reject_connection_request(request):
    if request.method == 'POST':
        try:
            request_id = request.POST.get('request_id')
            conn_request = ConnectionRequest.objects.get(
                id=request_id,
                to_user=request.user,
                status='pending'
            )
            conn_request.status = 'rejected'
            conn_request.save()
            return JsonResponse({'status': 'Request rejected'})
        except ConnectionRequest.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def get_connection_status(request, user_id):
    try:
        to_user = User.objects.get(id=user_id)
        status = 'none'
        
        # Check for pending request
        if ConnectionRequest.objects.filter(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        ).exists():
            status = 'pending_sent'
        elif ConnectionRequest.objects.filter(
            from_user=to_user,
            to_user=request.user,
            status='pending'
        ).exists():
            status = 'pending_received'
        # Check for existing connection
        elif ConnectionRequest.objects.filter(
            (Q(from_user=request.user, to_user=to_user) | 
             Q(from_user=to_user, to_user=request.user)),
            status='accepted'
        ).exists():
            status = 'connected'
            
        return JsonResponse({'status': status})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def my_network(request):
    received = ConnectionRequest.objects.filter(to_user=request.user, status='pending')
    connections = ConnectionRequest.objects.filter(
        (models.Q(from_user=request.user) | models.Q(to_user=request.user)),
        status='accepted'
    )
    return render(request, 'my_network.html', {
        'connection_requests': received,
        'connections': connections
    })

@login_required
def cancel_connection_request(request):
    if request.method == 'POST':
        try:
            request_id = request.POST.get('request_id')
            conn_request = ConnectionRequest.objects.get(
                id=request_id,
                from_user=request.user,
                status='pending'
            )
            user_id = conn_request.to_user.id
            conn_request.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Request cancelled successfully',
                'user_id': user_id
            })
        except ConnectionRequest.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
