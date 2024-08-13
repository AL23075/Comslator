from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm, SummarizeForm
from googletrans import Translator
from .languages import LANGUAGES
from django.http import JsonResponse
from .models import Message
from django.shortcuts import get_object_or_404

from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline
from django.utils import timezone
import pytz


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
            user_timezone = request.user.timezone  # Update this line based on your user model
            request.session['user_timezone'] = user_timezone
            timezone.activate(user_timezone)
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
            user_timezone = request.user.timezone  # Update this line based on your user model
            request.session['user_timezone'] = user_timezone
            timezone.activate(user_timezone)
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
    
    # Retrieve user's timezone from their profile, default to UTC if not set
    user_tz = pytz.timezone(request.user.timezone if request.user.timezone else 'UTC')
    
    # Convert message timestamps to user's timezone
    for message in room_messages:
        message.created = timezone.localtime(message.created, user_tz)
        message.updated = timezone.localtime(message.updated, user_tz)

    if request.method == 'POST':
        body = request.POST.get('body')
        if body.startswith('/b'):  # Bot command detected
            form = SummarizeForm(request.POST)
            if form.is_valid():
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']

                # Ensure start_time and end_time are timezone-aware
                if timezone.is_naive(start_time):
                    start_time = user_tz.localize(start_time)
                else:
                    start_time = start_time.astimezone(user_tz)
                
                if timezone.is_naive(end_time):
                    end_time = user_tz.localize(end_time)
                else:
                    end_time = end_time.astimezone(user_tz)

                # Convert start and end time to UTC for querying messages
                start_time_utc = start_time.astimezone(pytz.UTC)
                end_time_utc = end_time.astimezone(pytz.UTC)

                summary = summarize_chat(room_messages, start_time_utc, end_time_utc)

                Message.objects.create(
                    user=request.user,
                    room=room,
                    body=f"Summary:\n{summary}"
                )
                return redirect('room', pk=room.id)
        else:  # Regular message
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)

    else:
        form = SummarizeForm()

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
        'form': form,
    }
    return render(request, 'base/room.html', context)

# Load the summarization pipeline once when the server starts
summarizer = pipeline("summarization")

def summarize_chat(messages, start_time, end_time):
    # Convert to timezone-aware datetime if needed
    start_time = timezone.make_aware(start_time) if timezone.is_naive(start_time) else start_time
    end_time = timezone.make_aware(end_time) if timezone.is_naive(end_time) else end_time

    # Filter messages within the given time frame
    messages_to_summarize = messages.filter(
        created__gte=start_time, 
        created__lte=end_time
    )

    # Combine the messages into a single text
    text = "\n".join([f"{msg.created.strftime('%Y-%m-%d %H:%M:%S')} - {msg.body}" for msg in messages_to_summarize])
    
    if not text.strip():
        return "No content to summarize."

    try:
        # Generate the summary using the Hugging Face model
        summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
        summary_text = summary[0]['summary_text'].strip()
        return summary_text
    
    except Exception as e:
        return f"Error summarizing content: {str(e)}"
    

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

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
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


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})



def translation(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        source_language = request.POST.get('source_language')
        target_language = request.POST.get('target_language')
        
        translation = Translator()
        
        result = translation.translate(text, src=source_language, dest=target_language)
        
        return JsonResponse({'translate_text': result.text})
    return render(request, 'base/translation.html', {'languages': LANGUAGES})

translator = Translator()

def translate_message(request, message_id, target_lang):
    message = Message.objects.get(id=message_id)
    translated_text = translator.translate(message.body, dest=target_lang).text
    message.translated_body = translated_text
    message.save()
    return JsonResponse({'translated_text': translated_text})

def restore_message(request, message_id):
    message = Message.objects.get(id=message_id)
    original_text = message.body
    message.translated_body = None
    message.save()
    return JsonResponse({'original_text': original_text})

@csrf_exempt
def set_timezone(request):
    if request.method == 'POST':
        user_timezone = request.POST.get('timezone')
        request.session['user_timezone'] = user_timezone
        timezone.activate(user_timezone)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"})
