from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import CreateView,FormView,TemplateView,UpdateView,ListView,DetailView
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

from django.urls import reverse_lazy
from django.db.models import Q

from myapp.forms import SignupForm,SigninForm,ProfileEditForm,PostForm,CoverPicForm
from myapp.models import UserProfile,Posts,Comments

class SignUpView(CreateView):
    model=User
    form_class=SignupForm
    template_name="register.html"
    success_url=reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request,"account has been created!!")
        return super().form_valid(form)
    
    def form_invalid(self,form):
        messages.error(self.request,"failed to create account!")
        return super().form_invalid(form)
    
class SignInView(FormView):
    
    form_class=SigninForm
    template_name="login.html"
    

    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                return redirect("index")
            messages.error(request,"invalid credentials")
        return render(request,self.template_name,{"form":form})

class IndexView(CreateView,ListView):
    template_name="index.html"
    form_class=PostForm
    model=Posts
    context_object_name="posts"
    success_url=reverse_lazy("index")
    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)


class ProfileEditView(UpdateView):
    model=UserProfile
    form_class=ProfileEditForm
    template_name="profileedit.html"
    success_url=reverse_lazy('index')

# localhost:8000/posts/1/like/add/
def add_like_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    post_obj.liked_by.add(request.user)
    return redirect("index")

# localhost:8000/posts/{id}/comments/add/
def add_comment_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    comment=request.POST.get("comment")
    Comments.objects.create(user=request.user,post=post_obj,comment_text=comment)
    return redirect("index")


# localhost:8000/comments/{id}/remove
def remove_comment_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    comment_obj=Comments.objects.get(id=id)
    if request.user == comment_obj.user:
        comment_obj.delete()
        return redirect("index")
    else:
        messages.error(request,"plz contact admin")
        return redirect("signin")

class ProfileDetailview(DetailView):
   model=UserProfile
   template_name="profile.html"
   context_object_name="profile"
    

# profiles/{id}/coverpic/change
def change_cover_pic_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    prof_obj=UserProfile.objects.get(id=id)
    form=CoverPicForm(instance=prof_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profiledetail",pk=id)
    return redirect("profiledetail",pk=id)


class ProfileListView(ListView):
    model=UserProfile
    template_name="profile-list.html"
    context_object_name="profiles"

    # change query
    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user)

    # def get(self,request,*args,**kwargs):
    #     qs=UserProfile.objects.exclude(user=request.user)
    #     return render(request,self.template_name,{"profiles":qs})

    def post(self,request,*args,**kwargs):
        pname=request.POST.get("username")
        qs=UserProfile.objects.filter(Q(user__username__icontains=pname) | Q(user__first_name__icontains=pname))
        return render(request,self.template_name,{"profiles":qs})

# localhost:/profiles/{id}/follow/
def follow_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.add(profile_obj)
    user_prof.save()
    return redirect("index")

# localhost:/profiles/{id}/unfollow/
def unfollow_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.remove(profile_obj)
    user_prof.save()
    return redirect("index")

def post_delete_view(request,*args,**kwargs):
    post_id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=post_id)
    post_obj.delete()
    return redirect("index")