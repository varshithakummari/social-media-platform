from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Profile

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'social/register.html', {'form': form})

@login_required
def feed(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect('feed')
    
    # Render all updates descending by timeline creation
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'social/feed.html', {'posts': posts})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    # Redirect gracefully to the page user initiated actions from
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(post=post, user=request.user, text=text)
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    user_posts = target_user.posts.all().order_by('-created_at')
    
    # Logic checking parameters safely
    is_following = request.user.profile.following.filter(id=target_user.profile.id).exists()
    
    context = {
        'target_user': target_user,
        'user_posts': user_posts,
        'is_following': is_following
    }
    return render(request, 'social/profile.html', context)

@login_required
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user != request.user:
        user_profile = request.user.profile
        target_profile = target_user.profile
        if user_profile.following.filter(id=target_profile.id).exists():
            user_profile.following.remove(target_profile)
        else:
            user_profile.following.add(target_profile)
    return redirect('profile', username=username)
