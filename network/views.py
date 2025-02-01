from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Profile


def index(request):
    allposts = Post.objects.all().order_by("timestamp").reverse()

    #pagination
    paginator = Paginator(allposts, 10)
    pagenumber = request.GET.get('page')
    inpage = paginator.get_page(pagenumber)
    return render(request, "network/index.html", {
        "allposts": allposts,
        "inpage": inpage
    })

def profile(request, name):
    try:
        user = User.objects.get(username=name)
        profile = Profile.objects.get(user=user)
        users_profile = Profile.objects.get(user=request.user)
    except:
        return render(request, 'network/profile.html', {"error": True})
    allposts = Post.objects.filter(user=user).order_by('-timestamp')
    paginator = Paginator(allposts, 10)
    if request.GET.get("page") != None:
        try:
            allposts = paginator.page(request.GET.get("page"))
        except:
            allposts = paginator.page(1)
    else:
        allposts = paginator.page(1)
    for i in users_profile.follower.all():
        print(i)
    context = {
        'allposts': allposts,
        "user": user,
        "profile": profile,
        'users_profile': users_profile
    }
    return render(request, 'network/profile.html', context)

def newpost(request):
    if request.method == "POST":

        # Getting the data of new post
        content = request.POST["content"]
        user = User.objects.get(pk=request.user.id)
        posting = Post(content=content, user=user)
        posting.save()
        return HttpResponseRedirect(reverse("index"))

@csrf_exempt
@login_required 
def editpost(request):
    if request.method == "POST":
        # Getting the data of the post
        post_id = request.POST.get('id')
        new_content = request.POST.get('post')
        try: 
            post = Post.objects.get(id=post_id)
            if post.user == request.user:
                post.content = new_content.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)
    return JsonResponse({}, status=400)

@csrf_exempt
@login_required
def follow(request):
    if request.method == "POST":
        user = request.POST.get('user')
        action = request.POST.get('action')

        if action == 'Follow':
            try:
                # add user to current user's following list
                user = User.objects.get(username=user)
                profile = Profile.objects.get(user=request.user)
                profile.following.add(user)
                profile.save()

                # add current user to  user's follower list
                profile = Profile.objects.get(user=user)
                profile.follower.add(request.user)
                profile.save()
                return JsonResponse({'status': 201, 'action': "Unfollow", "follower_count": profile.follower.count()}, status=201)
            except:
                return JsonResponse({}, status=404)
        else:
            try:
                # remove user from current user's following list
                user = User.objects.get(username=user)
                profile = Profile.objects.get(user=request.user)
                profile.following.remove(user)
                profile.save()

                # remove current user from  user's follower list
                profile = Profile.objects.get(user=user)
                profile.follower.remove(request.user)
                profile.save()
                return JsonResponse({'status': 201, 'action': "Follow", "follower_count": profile.follower.count()}, status=201)
            except:
                return JsonResponse({}, status=404)
    return JsonResponse({}, status=400)

@csrf_exempt
@login_required
def following(request):
    following = Profile.objects.get(user=request.user).following.all()
    allposts = Post.objects.filter(user__in=following).order_by("timestamp").reverse()

    #pagination
    paginator = Paginator(allposts, 10)
    pagenumber = request.GET.get('page')
    inpage = paginator.get_page(pagenumber)
    return render(request, "network/following.html", {
        "allposts": allposts,
        "inpage": inpage
    })

@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        is_liked = request.POST.get('is_liked')
        try:
            post = Post.objects.get(id=post_id)
            if is_liked == 'no':
                post.like.add(request.user)
                is_liked = 'yes'
            elif is_liked == 'yes':
                post.like.remove(request.user)
                is_liked = 'no'
            post.save()

            return JsonResponse({'like_count': post.like.count(), 'is_liked': is_liked, "status": 201})
        except:
            return JsonResponse({'error': "Post not found", "status": 404})
    return JsonResponse({}, status=400)



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile = Profile(user=user)
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
