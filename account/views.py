from django.shortcuts import render,redirect
from django.views import View

from .forms import SignupForm, LoginForm
from images.models import Links,Images
from django.contrib.auth import login, authenticate,logout

from django.http import HttpResponse
import os

# Create your views here.
class Index(View):
    def get(self,request):
        return render(request,'index.html')

class LoginView(View):
    def get(self,request):
        form = LoginForm()
        return render(request,'LoginForm.html',{'form':form})
    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('../home/')
            else:
                return HttpResponse("<script>window.location.href = './'; alert('Incorrect UserName/Password');</script>")
        else:
            return render(request, 'LoginForm.html', {'form': form,'field.errors':form.errors})

class SignupView(View):
    def post(self,request):
        form = SignupForm(request.POST)
        if form.is_valid():
            ins = form.save(commit=False)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            if not os.path.exists('./media/ImageData/' + username + '/'):
                os.mkdir('./media/ImageData/' + username + '/')
                os.mkdir('./media/ImageData/'+username+'/All/')
                os.mkdir('./media/ImageData/'+username+'/thumb/')
            ins.save()
            user = authenticate(username=username,password=password)
            if user is not None:
                ins_link = Links.objects.create(user=user,link={'face_keys': [], })
                ins_link.save()
                ins.save()
                login(request,user)
                return redirect('../home/')
            else:
                return HttpResponse('<script>alert("Some Error Occur")</script>')
        else:
            return render(request, 'SignupForm.html', {'form': form,'field.errors':form.errors})
    def get(self,request):
        form = SignupForm()
        return render(request,'SignupForm.html',{'form':form})


class HomeView(View):
    def get(self, request):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            ins  = Links.objects.get(user=user)
            FaceFolder = ins.link['face_keys']
            folders = list(ins.link.keys())
            folders.remove('face_keys')
            folders = [i for i in folders if i not in FaceFolder]
        except:
            folders = os.listdir('./media/ImageData/' + str(user) + '/')
        return render(request,'HomePage.html',{'facefolder':FaceFolder,'folders':folders})

class MainPage(View):
    def get(self, request):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        return render(request,'MainPage.html',{'name':str(user)})


class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponse("<script>window.location.href = '../';alert('Logged out successfully!');</script>")