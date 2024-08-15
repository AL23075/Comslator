import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, Task
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from .models import Message
from django.shortcuts import get_object_or_404

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            user.status = 'online'
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    User.status = 'offline'
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)



def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        room.participants.add(request.user)
        return redirect('home')
    
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required
def updateUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', request.user.id)
    else:
        form = UserForm(instance=request.user)
    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})

@login_required(login_url='login')
def task_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.user not in room.participants.all():
        messages.error(request, "You are not allowed to view tasks.")
        return redirect('home')
    
    if request.method == 'POST':
        if request.user == room.host:
            task_title = request.POST.get('task_title')
            task_description = request.POST.get('task_description')
            Task.objects.create(title=task_title, description=task_description, user=request.user, room=room)
            messages.success(request, "Task added successfully!")  # Thông báo thành công khi thêm task
        else:
            return HttpResponseForbidden("You are not allowed to add tasks.")
        return redirect('task_view', room_id=room.id)

    tasks = Task.objects.filter(room=room)
    return render(request, 'base/task.html', {'tasks': tasks, 'room': room})

@login_required(login_url='login')
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Kiểm tra xem người dùng có phải là thành viên của phòng hay không
    if request.user not in task.room.participants.all():
        messages.error(request, "You are not allowed to mark tasks as completed.")
        return redirect('home')
    
    if request.user not in task.completed_by.all():
        task.completed_by.add(request.user)  # Thêm người dùng vào danh sách hoàn thành
        messages.success(request, "Task marked as completed!")  # Thông báo hoàn thành task
    else:
        task.completed_by.remove(request.user)  # Xóa người dùng khỏi danh sách hoàn thành
        messages.success(request, "Task unmarked as completed!")  # Thông báo bỏ đánh dấu hoàn thành
    
    task.save()
    return redirect('task_view', room_id=task.room.id)

@login_required(login_url='login')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.user != task.room.host:
        return HttpResponseForbidden("You are not allowed to delete tasks.")
    
    task.delete()
    messages.success(request, "Task deleted successfully!")  # Thông báo khi task bị xóa
    return redirect('task_view', room_id=task.room.id)

@login_required(login_url='login')
def callRoom(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Kiểm tra xem người dùng có phải là participant không
    if request.user not in room.participants.all():
        messages.error(request, "You are not allowed to join this call.")
        return redirect('home')

    # Kiểm tra xem đã có call room chưa
    if room.call_room_id is None:
        room.call_room_id = str(uuid.uuid4())  # Tạo ID duy nhất cho cuộc gọi
        room.save()

    return render(request, 'base/call_room.html', {'room': room})
