from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from . import keys
from isodate import parse_duration
import requests
import bcrypt
from .models import *
from googleapiclient.discovery import build
import json

service     = build('youtube', 'v3', developerKey=keys.YOUTUBE_DATA_API_KEY)
collection  = service.search()

#Create your views here.
def index(request):
    return render(request, "landing/landing.html")

def interests(request):

    if("user_id" not in request.session):
        messages.error(request, "You must be logged in in order to access this page. Rules are rules")
        return redirect("/")

    # if("loggedInUser_id" not in request.session):
    #     messages.error(request, "You must be logged in in order to access this page. Rules are rules")
    #     return redirect("/")

    else:

        loggedInUser    = User.objects.get(id=request.session["user_id"])

        context={
            "loggedInUser"  : loggedInUser,
            "all_users"     : User.objects.all()
        }
        return render(request, "spot/index.html", context)

def register(request):
    
    errors = User.objects.basic_validator(request.POST)

    if len(errors) > 0:
        request.session['firstName']    = request.POST['firstName']
        request.session['lastName']     = request.POST['lastName']
        request.session['email']        = request.POST['email']
        request.session['username']     = request.POST['username']
        request.session['password']     = request.POST['password']
        request.session['confirm']      = request.POST['confirm']
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
        # redirect the user back to the form to fix the errors
        return redirect('/')

    else:
        hash_pw                         = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        firstName                       = request.POST['firstName']
        lastName                        = request.POST['lastName']
        email                           = request.POST['email']
        username                        = request.POST['username']
        password                        = request.POST['password']
        confirm                         = request.POST['confirm']


        # checking for duplicate data in database
        if(User.objects.filter(email=email).exists()):
            messages.error(request, "That email is already taken, sorry.")
            return redirect("/")
        if(User.objects.filter(username=username).exists()):
            messages.error(request, "That username is already taken, sorry.")
            return redirect("/")

        else: 

            User.objects.create(firstName=firstName, lastName=lastName, email=email, username=username, password=hash_pw)

            createdUser = User.objects.last()

            request.session['user_id']   = createdUser.id

            messages.success(request, "User Created Successfully :)")

            return redirect("/interests")

def login(request):
    
    errors = User.objects.login_validator(request.POST)

    if len(errors) > 0:
        request.session['username']     = request.POST['username']
        request.session['password']     = request.POST['password']
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
        # redirect the user back to the form to fix the errors
        return redirect('/')
    else:
        username                        = request.POST['username']
        password                        = request.POST['password']
        
        user_set = User.objects.filter(username=username)
        user = user_set[0]

        if bcrypt.checkpw(password.encode(), user.password.encode()):
            request.session['user_id']   = user.id
            messages.success(request, f"Welcome back, {user.firstName}")
            return redirect("/interests")
        else:   
            messages.error(request, "Password did not match with any User in database, sorry try again!")
            return redirect("/")

def logout(request):
    request.session.flush()

    messages.success(request, "Logged out :)")
    return redirect("/")




def getVideos(request):

    if("user_id" not in request.session):
        messages.error(request, "You must be logged in in order to access this page. Rules are rules")
        return redirect("/")

    else:
        videos = []

        if request.method == 'POST':
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            video_url = 'https://www.googleapis.com/youtube/v3/videos'


            search_params = {
                'part' : 'snippet',
                'q' : request.POST['search'],
                'key' : keys.YOUTUBE_DATA_API_KEY,
                'maxResults' : 9,
                'type' : 'video'
            }

            r = requests.get(search_url, params=search_params)

            results = r.json()['items']

            video_ids = []
            for result in results:
                video_ids.append(result['id']['videoId'])

            if request.POST['submit'] == 'lucky':
                return redirect(f'https://www.youtube.com/watch?v={ video_ids[0] }')

            video_params = {
                'key' : keys.YOUTUBE_DATA_API_KEY,
                'part' : 'snippet,contentDetails',
                'id' : ','.join(video_ids),
                'maxResults' : 9
            }

            r = requests.get(video_url, params=video_params)

            results = r.json()['items']

            
            for result in results:
                video_data = {
                    'title' : result['snippet']['title'],
                    'id' : result['id'],
                    'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                    'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                    'thumbnail' : result['snippet']['thumbnails']['high']['url']
                }

                videos.append(video_data)

        loggedInUser    = User.objects.get(id=request.session["user_id"])

        context={
            "loggedInUser"  : loggedInUser,
            "all_users"     : User.objects.all(),
            'videos' : videos
        }
        
        return render(request, 'spot/video-landing.html', context)


def otherInterest(request):
    if("user_id" not in request.session):
        messages.error(request, "You must be logged in in order to access this page. Rules are rules")
        return redirect("/")

    loggedInUser    = User.objects.get(id=request.session["user_id"])

    context={
        "loggedInUser"  : loggedInUser,
        "all_users"     : User.objects.all(),
    }
    return render(request, "spot/interests.html", context)


def interestSearch(request):

    if("user_id" not in request.session):
        messages.error(request, "You must be logged in in order to access this page. Rules are rules")
        return redirect("/")

    #Ciso code
    response = collection.list(part='snippet', q='climate change', type='video').execute()
    print (json.dumps(response, sort_keys=True, indent=4))

    video_id_results = []

    for item in response['items']:
        video_id_results.append(item['snippet']['thumbnails']['default'])
        
    print(video_id_results)

    #code from the other day
    search = request.POST['search']

    print(request.POST)

    query_string = ""

    for term in request.POST.getlist('search'):
        query_string += f"{term}%20"

    print(query_string)


    context = {
        'ids': video_id_results,
        "search": search
    }

    return render(request, 'spot/video-landing.html', context)
    
def wall(request):
    return render(request, 'spot/wall.html')