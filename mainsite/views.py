from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from mainsite.models import Card
from bs4 import BeautifulSoup
import requests

def index(request):
    return render_to_response('base.html', {'user': request.user})

def login_view(request):
    if request.method != 'POST':
        return render_to_response('login.html', {'user': request.user}, context_instance=RequestContext(request))
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            pass
            # Return an 'invalid login' error message.

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/login/")
    else:
        form = UserCreationForm()
    return render_to_response("register.html", {
        'form': form,
        'user': request.user,
    }, context_instance=RequestContext(request))

def card_info(request, card_name, set_name):
        card = Card.objects.get(name__iexact=card_name)
        _set = card.sets.all()[0]
        return render_to_response('card_info.html', {'card': card, 'set': _set,'user':request.user})

def top_decks(request):
    r = requests.get("http://www.starcitygames.com/pages/decklists/")
    soup = BeautifulSoup(r.text)

    top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']
    
    return HttpResponse(BeautifulSoup(requests.get(top).text).find('section', id="content").table)
