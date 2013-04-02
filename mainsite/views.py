from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from mainsite.models import Card, Deck, PublishedDeck, CardCount, Card, FavoriteCard
from bs4 import BeautifulSoup
import requests
from django.contrib.auth.models import User
from haystack.query import SearchQuerySet
from datetime import datetime

def index(request):
    r = requests.get("http://www.starcitygames.com/pages/decklists/")
    soup = BeautifulSoup(r.text)

    top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']

    table = BeautifulSoup(requests.get(top).text).find('section', id="content").table
    rows = ['<a href="%s">%s</a>' % (row.a['href'], row.strong.text) for row in table.findAll('tr')[5:13]] 

    recent = PublishedDeck.objects.all().order_by('-published')
    context = {'user': request.user, 'rows':rows, 'recent':recent}
    return render_to_response('home.html', context)

def about(request):
    return render_to_response('about.html', {'user': request.user})

def profile(request, username):
    user = User.objects.all().get(username=username)
    favorite = FavoriteCard.objects.all().get(user=user)
    if favorite:
        favorite_img = favorite.card.get_image_url(favorite.card.sets.all()[0])
    else:
        favorite_img = None
    decks = Deck.objects.filter(user=user)
    published = PublishedDeck.objects.filter(user=user)[:10]
    context = {'username': username, 'decks':decks, 'published':published, 'user':user,'favorite':favorite_img}
    return render_to_response('profile.html', context)

def decks(request):
    decks = Deck.objects.filter(user=request.user)
    selected = request.GET.get('deck')
    addCard = request.GET.get('addCard')
    removeCard = request.GET.get('removeCard')
    new = request.GET.get('new')
    publish = request.GET.get('publish')
    if new:
        new = Deck(name=new,user=request.user,created=datetime.now(),description='')
        new.save()
        deck = None
    elif selected:
        deck = Deck.objects.all().get(pk=selected)
        if addCard:
            card = Card.objects.all().get(pk=addCard)
            if deck.card_counts.filter(card=card):
                count = deck.card_counts.get(card=card)
                count.multiplicity += 1
                count.save()
            else:
                count = CardCount(card=card, multiplicity=1)
                count.save()
                deck.card_counts.add(count)
        elif removeCard:
            count = CardCount.objects.all().get(pk=removeCard)
            if count.multiplicity > 1:
                count.multiplicity -= 1
                count.save()
            else:
                deck.card_counts.remove(count)
        elif publish:
            new = PublishedDeck(name=deck.name,user=request.user,published=datetime.now(),description='',score=0)
            new.save()
            for count in deck.card_counts.all():
                new_count = CardCount(card=count.card, multiplicity=count.multiplicity)
                new_count.save()
                new.card_counts.add(new_count)
            new.save()

    else:
        deck = None
    query = request.GET.get('query')
    if query:
        results = SearchQuerySet().filter(content=query)
    else:
        results = ''
    context = {
            'user':request.user, 
            'decks': decks,
            'deck': deck,
            'results':results
            }
    return render_to_response('decks.html', context)

def published(request, deck_id):
    deck = PublishedDeck.objects.all().get(pk=deck_id)
    context = {
            'user':request.user, 
            'description': deck.description, 
            'deck':deck,
            'card_counts':deck.card_counts,
            'decks': decks,
            }
    return render_to_response('published.html', context)

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

def change_favorite(request, card_name):
    user = request.user
    new_card = Card.objects.all().get(name=card_name)
    try:
        favorite = FavoriteCard.objects.all().get(user=user)
    except:
        favorite = FavoriteCard(user=user,card=new_card)
    favorite.card = new_card
    favorite.save()
    return HttpResponseRedirect('/profile/%s' % user.username)

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
        return render_to_response('card_info.html', {'card': card, 'set': _set,'user':request.user, 'card_image_url':card.get_image_url(_set),'sets':card.sets.all()})

def top_decks(request):
    r = requests.get("http://www.starcitygames.com/pages/decklists/")
    soup = BeautifulSoup(r.text)

    top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']

    table = BeautifulSoup(requests.get(top).text).find('section', id="content").table
    rows = table.findAll('td', {'class':'deckdbbody2'}, limit=8)
    
    return HttpResponse(table)
