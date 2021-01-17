from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import TodoForm
from .models import Todo

def home(request):
    return render(request,'todo/home.html')

def loginuser(request):
    if request.method=='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username,password=password)
            if user is None:
                return render(request,'todo/login.html',{'form':form, 'error':'Either UserName or Password are not correct'})
            else:
                login(request,user)
                return redirect('currenttodos')
        else:
            print("form is invalid")
    else:
        form = AuthenticationForm()  
    return render(request,'todo/login.html',{'form':form})

def signupuser(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        username=request.POST['username']
        password1=request.POST['password1']
        password2=request.POST['password2']

        if password1 == password2:
            try :
                user = User.objects.create_user(username=username, password=password1)
                user.save()
                login(request,user)
                return redirect('currenttodos')
            except Exception as e:
                return render(request,'todo/signup.html',{'form':form,'error':'Username Exists'})
        else:
            return render(request,'todo/signup.html',{'form':form,'error':'password doesnt match'})
    else:
        form = UserCreationForm()
    return render(request,'todo/signup.html',{'form':form})

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'todo/current.html',{'todos':todos})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'todo/completedtodos.html',{'todos':todos})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance = todo)
        return render(request,'todo/viewtodo.html',{'todo':todo,'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todo,'form':form,'error':'Bad info'})

@login_required
def logoutuser(request):
    if request.method=='POST':
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method == 'POST':
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todo/createtodo.html',{'form':form,'error':'Values mismatched! Try again.'})
    else:
        form = TodoForm()
    return render(request,'todo/createtodo.html',{'form':form})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')