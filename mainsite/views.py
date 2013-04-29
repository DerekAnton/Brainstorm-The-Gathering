from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from mainsite.models import Card, Deck, PublishedDeck, CardCount, Card, FavoriteCard, Comment, Collection, Set, Card_Breakdown, Format
from bs4 import BeautifulSoup
import requests
import random
from django.contrib.auth.models import User
from haystack.query import SearchQuerySet
from datetime import datetime
import urllib
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def index(request):
    r = requests.get("http://www.starcitygames.com/pages/decklists/")
    soup = BeautifulSoup(r.text)

    top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']

    #table = BeautifulSoup(requests.get(top).text).find('section', id="content").table
    #rows = ['<a href="%s">%s</a>' % (row.a['href'], row.strong.text) for row in table.findAll('tr')[5:13]] 

    recent = PublishedDeck.objects.all().order_by('-published')
    #context = {'user': request.user, 'rows':rows, 'recent':recent}
    context = {'user': request.user, 'recent':recent}
    return render_to_response('home.html', context)

def about(request):
    return render_to_response('about.html', {'user': request.user})

def simulate(request):
    select = request.GET.get('select')
    if select:
        deck = Deck.objects.get(pk=select)
        deckList = []
        for card_count in deck.card_counts.all():
            for i in xrange(card_count.multiplicity):
                deckList.append(card_count.card)
        try:
            hand = random.sample(deckList, 7)
        except ValueError:
            hand = deckList
        images = []
        for card in hand:
            images.append(card.get_image_url())
        return render_to_response('simulate.html', {'user': request.user, 'decks':Deck.objects.filter(user=request.user), 'images':images})
    return render_to_response('simulate.html', {'user': request.user, 'decks':Deck.objects.filter(user=request.user)})

def profile(request, username):
    user = User.objects.all().get(username=username)
    if FavoriteCard.objects.all().filter(user=user):
        favorite = FavoriteCard.objects.all().get(user=user)
        favorite_img = favorite.card.get_image_url(favorite.card.sets.all()[0])
    else:
        favorite_img = None
    decks = Deck.objects.filter(user=user)
    published = PublishedDeck.objects.filter(user=user)[:10]
    context = {'username': username, 'decks':decks, 'published':published, 'user':user,'favorite':favorite_img}
    return render_to_response('profile.html', context)

def advanced(request):
    name = request.GET.get('name')
    sets = request.GET.get('set')
    color = request.GET.get('color')
    power = request.GET.get('power')
    toughness = request.GET.get('toughness')
    types = request.GET.get('type')
    sub = request.GET.get('sub')
    supers = request.GET.get('super')

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    sqs = SearchQuerySet().models(Card).filter(content=name).order_by('text')
    if sets:
        sqs = sqs.filter(sets=sets)
    if color:
        sqs = sqs.filter_and(color=color)
    if power:
        sqs = sqs.filter(power=power)
    if toughness:
        sqs = sqs.filter(toughness=toughness)
    if types:
        sqs = sqs.filter(types=types)
    if sub:
        sqs = sqs.filter(subs=sub)
    if supers:
        sqs = sqs.filter(supers=supers)
    paginator = Paginator(sqs, 20)
    try:
        results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        results = paginator.page(paginator.num_pages)
    context = {'results':results}
    return render_to_response('advanced.html', context)

def decks(request):
    multiplicity = request.GET.get('multiplicity')
    sbMultiplicity = request.GET.get('sbMultiplicity')
    collectionMultiplicity = request.GET.get('collectionMultiplicity')
    deckSet = request.GET.get('deckSet')
    collectionSet = request.GET.get('collectionSet')
    sbSet = request.GET.get('sbSet')
    decks = Deck.objects.filter(user=request.user)
    collection = request.GET.get('collection')
    selected = request.GET.get('deck')
    #addCard = request.GET.get('addCard')
    removeCard = request.GET.get('removeCard')
    removeCardSb = request.GET.get('removeCardSb')
    decriment = request.GET.get('decriment')
    decrimentCollection = request.GET.get('decrimentCollection')
    decrimentSb = request.GET.get('decrimentSb')
    new = request.GET.get('new')
    publish = request.GET.get('publish')
    collectionAdd = request.GET.get('collectionAdd')
    sbAdd = request.GET.get('sbAdd')
    #collectionRemove = request.GET.get('collection_remove')
    removeCardCollection = request.GET.get('removeCardCollection')
    deckAdd = request.GET.get('deckAdd')
    collectionAdd = request.GET.get('collectionAdd')
    delete_deck = request.GET.get('deck_delete')
    query = request.GET.get('query')
    deck = None


    if Collection.objects.all().filter(user=request.user):
        userCollection = Collection.objects.all().filter(user=request.user)[0]
    else:
        newCollection = Collection(user=request.user)
        newCollection.save()
        userCollection = newCollection
    if new:
        new = Deck(name=new,user=request.user,created=datetime.now(),description='')
        new.save()
        deck = new
    elif selected:
        deck = Deck.objects.all().get(pk=selected)
        if deckAdd or collectionAdd or sbAdd:
            if deckAdd:
                card = Card.objects.all().get(pk=deckAdd)
            elif collectionAdd:
                card = Card.objects.all().get(pk=collectionAdd)
            else:
                card = Card.objects.all().get(pk=sbAdd)
            if deckAdd:
                if deck.card_counts.filter(card=card):
                    count = deck.card_counts.get(card=card)
                    count.multiplicity += 1
                    count.save()
                else:
                    count = CardCount(card=card, multiplicity=1)
                    count.save()
                    deck.card_counts.add(count)
            elif collectionAdd:
                if userCollection.card_counts.filter(card=card):
                    count = userCollection.card_counts.get(card=card)
                    count.multiplicity += 1
                    count.save()
                else:
                    count = CardCount(card=card, multiplicity=1)
                    count.save()
                    userCollection.card_counts.add(count)
            elif sbAdd:
                if deck.sb_counts.filter(card=card):
                    count = deck.sb_counts.get(card=card)
                    count.multiplicity += 1
                    count.save()
                else:
                    count = CardCount(card=card, multiplicity=1)
                    count.save()
                    deck.sb_counts.add(count)
        if decriment:
            count = deck.card_counts.get(pk=decriment)
            if count.multiplicity > 1:
                count.multiplicity -= 1
                count.save()
            else:
                deck.card_counts.remove(count)
        if decrimentSb:
            count = deck.sb_counts.get(pk=decrimentSb)
            if count.multiplicity > 1:
                count.multiplicity -= 1
                count.save()
            else:
                deck.sb_counts.remove(count)
        if removeCard:
            count = CardCount.objects.all().get(pk=removeCard)
            deck.card_counts.remove(count)
        if removeCardSb:
            count = CardCount.objects.all().get(pk=removeCardSb)
            deck.sb_counts.remove(count)
        if publish:
            new = PublishedDeck(name=deck.name,user=request.user,published=datetime.now(),description='',score=0)
            new.save()
            for count in deck.card_counts.all():
                new_count = CardCount(card=count.card, multiplicity=count.multiplicity)
                new_count.save()
                new.card_counts.add(new_count)
            new.save()
            for count in deck.sb_counts.all():
                new_count = CardCount(card=count.card, multiplicity=count.multiplicity)
                new_count.save()
                new.sb_counts.add(new_count)
            new.save()
            standard = Format.objects.filter(name='standard')[0]
            modern = Format.objects.filter(name='modern')[0]
            legacy = Format.objects.filter(name='legacy')[0]
            vintage = Format.objects.filter(name='vintage')[0]
            commander = Format.objects.filter(name='commander')[0]
            breakdown = Card_Breakdown(deck=new, number_of_cards=0)
            breakdown.initialize(new)
            breakdown.save()
            new.standard_legal = standard.legal(deck)
            new.modern_legal = modern.legal(deck)
            new.legacy_legal = legacy.legal(deck)
            new.vintage_legal = vintage.legal(deck)
            new.commander_legal = commander.legal(deck)
            new.save()
    elif collectionAdd:
        card = Card.objects.all().get(pk=collectionAdd)
        if not userCollection.card_counts.filter(card=card):
            userCollection.card_counts.add(CardCount.objects.get_or_create(card=card, multiplicity=1)[0])
        else:
            multiplicity = userCollection.card_counts.filter(card=card)[0].multiplicity+1
            if userCollection.card_counts.filter(card=card):
                userCollection.card_counts.remove(userCollection.card_counts.filter(card=card)[0])
            userCollection.card_counts.add(CardCount.objects.get_or_create(card=card, multiplicity=multiplicity)[0])
    elif removeCardCollection:
        if userCollection.card_counts.filter(card=Card.objects.filter(name=removeCardCollection)[0]):
            userCollection.card_counts.remove(userCollection.card_counts.filter(card=Card.objects.filter(name=removeCardCollection)[0])[0])
    elif decrimentCollection:
        count = userCollection.card_counts.get(pk=decrimentCollection)
        if count.multiplicity > 1:
            count.multiplicity -= 1
            count.save()
        else:
            userCollection.card_counts.remove(count)
    elif collectionSet:
        count = userCollection.card_counts.get(pk=collectionSet)
        count.multiplicity = collectionMultiplicity
        count.save()
    if deckSet:
        count = CardCount.objects.all().get(pk=deckSet)
        count.multiplicity = multiplicity
        count.save()
    if sbSet:
        count = CardCount.objects.all().get(pk=sbSet)
        count.multiplicity = sbMultiplicity
        count.save()
    if query:
        results = SearchQuerySet().models(Card).filter(content=query)
    else:
        results = ''
    if delete_deck and Deck.objects.all().filter(pk=delete_deck):
        if (Deck.objects.all().get(pk=delete_deck).user == request.user):
            Deck.objects.all().get(pk=delete_deck).delete()
    deckSizes = {}
    for currentDeck in decks:
        size = 0
        for card_count in currentDeck.card_counts.all():
            size += card_count.multiplicity
        deckSizes[currentDeck.pk] = size
    creatures = []
    lands = []
    spells = []
    perm = []
    if deck:
        for card_count in deck.card_counts.all():
            card = card_count.card
            if card.typing.filter(name='Creature'):
                creatures.append(card_count)
            elif card.typing.filter(name='Land'):
                lands.append(card_count)
            elif card.typing.filter(name='Sorcery'):
                spells.append(card_count)
            elif card.typing.filter(name='Instant'):
                spells.append(card_count)
            else:
                perm.append(card_count)
    context = {
            'creatures':creatures,
            'lands':lands,
            'spells':spells,
            'perm':perm,
            'user':request.user, 
            'decks': decks,
            'deck': deck,
            'results': results,
            'collection': userCollection,
            'deckSizes':deckSizes
            }
    return render_to_response('decks.html', context)

def published(request, deck_id):
    deck = PublishedDeck.objects.all().get(pk=deck_id)
    new_comment = request.GET.get('new_comment')
    username=request.GET.get('user')
    grab = request.GET.get('grabDeck')
    grabID = request.GET.get('deck')
    try:
        user=User.objects.all().get(username=username)
    except:
        user=None
    if new_comment:
        new_comment = Comment(user=user, published_deck=deck, timestamp=datetime.now(), message=new_comment)
        new_comment.save()
        new_comment = None
    if grab and grabID:
        grab = PublishedDeck.objects.all().get(pk=grabID)
        new = Deck(name=grab.name,user=request.user,created=datetime.now(),description='')
        new.save()
        for count in grab.card_counts.all():
            new_count = CardCount(card=count.card, multiplicity=count.multiplicity)
            new_count.save()
            new.card_counts.add(new_count)
        for count in grab.sb_counts.all():
            new_count = CardCount(card=count.card, multiplicity=count.multiplicity)
            new_count.save()
            new.sb_counts.add(new_count)




    curve = Card_Breakdown.objects.filter(deck=deck)[0].mana_curve
    curve = curve.split(', ')
    creatures = []
    lands = []
    spells = []
    perm = []
    if deck:
        for card_count in deck.card_counts.all():
            card = card_count.card
            if card.typing.filter(name='Creature'):
                creatures.append(card_count)
            elif card.typing.filter(name='Land'):
                lands.append(card_count)
            elif card.typing.filter(name='Sorcery'):
                spells.append(card_count)
            elif card.typing.filter(name='Instant'):
                spells.append(card_count)
            else:
                perm.append(card_count)
    context = {
        'standard':deck.standard_legal,
        'modern':deck.modern_legal,
        'legacy':deck.legacy_legal,
        'vintage':deck.vintage_legal,
        'commander':deck.commander_legal,
        #'curvelength':curvelength,
        #'manacurve':manacurve,
        'creatures':creatures,
        'lands':lands,
        'spells':spells,
        'perm':perm,
        'breakdown':Card_Breakdown.objects.filter(deck=deck)[0],
        'user':request.user, 
        'description': deck.description, 
        'deck':deck,
        'sb_counts':deck.sb_counts,
        'card_counts':deck.card_counts,
        'decks': decks,
        'comments': Comment.objects.filter(published_deck=deck)#user, timestamp, message 
        }
    for i in xrange(len(curve)):
        context['var'+str(i)] = int(curve[i])
        #print 'var'+str(i)+'='+str(int(curve[i]))
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
            return HttpResponseRedirect('/')
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
        name=request.POST['username']
        pw=request.POST['password']
        pw2=request.POST['password2']
        email=request.POST['email']
        message=''
        if User.objects.filter(username=name):
            message = message + 'Username taken\n'
        if email and User.objects.filter(email=email):
            message = message + 'Email taken\n'
        if pw != pw2:
            message = message + 'Passwords do not match\n'
        print message
        if message == '':
            newUser = User(username=name,password=make_password(pw))
            if email:
                newUser.email=email
            newUser.save()
            coll=Collection(user=newUser)
            coll.save()
            newUser=authenticate(username=name, password=pw)
            login(request,newUser)
            return HttpResponseRedirect('/')
        return render_to_response("register.html", {
            'user': request.user,
            'message': message,
            }, context_instance=RequestContext(request))
    return render_to_response("register.html", {
        'message': '',
        'user': request.user,
    }, context_instance=RequestContext(request))

def card_info(request, card_name, set_name):
    card = Card.objects.get(name__iexact=card_name)
    _set = Set.objects.get(name=set_name)
    standard = Format.objects.filter(name='standard')[0]
    modern = Format.objects.filter(name='modern')[0]
    legacy = Format.objects.filter(name='legacy')[0]
    vintage = Format.objects.filter(name='vintage')[0]
    commander = Format.objects.filter(name='commander')[0]
    #formats = [standard, modern, legacy, vintage, commander]
    inStandard = standard.checkCard(card)
    inModern = modern.checkCard(card)
    inLegacy = legacy.checkCard(card)
    inVintage = vintage.checkCard(card)
    inCommander = commander.checkCard(card)
    #for format in formats:
    #    format = format.checkCard(card)
    params = {'cards': card_name}
    params2 = {'cn': card_name}
    types = card.typing.all()
    supertypes = card.super_typing.all()
    subtypes = card.sub_typing.all()
    price_url = 'http://magic.tcgplayer.com/db/magic_single_card.asp?' + urllib.urlencode(params2)
    price_query = urllib.urlencode(params)
    return render_to_response('card_info.html', {'standard':inStandard, 'modern':inModern, 'legacy':inLegacy, 'vintage':inVintage, 'commander':inCommander, 'supertypes': supertypes, 'subtypes': subtypes, 'card': card, 'types':types, 'set': _set,'user':request.user, 'card_image_url':card.get_image_url(_set),'sets':card.sets.all(), 'price_query': price_query, 'price_url': price_url, 'isCreature': len(card.typing.filter(name='Creature')) == 1})

def top_decks(request):
    r = requests.get("http://www.starcitygames.com/pages/decklists/")
    soup = BeautifulSoup(r.text)

    top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']

    table = BeautifulSoup(requests.get(top).text).find('section', id="content").table
    rows = table.findAll('td', {'class':'deckdbbody2'}, limit=8)
    
    return HttpResponse(table)

def add_comment(request):
    comment = Comment(user=request.commenter, published_deck=request.deck, timestamp=request.time, message=request.message)
    comment.save()

    return HttpResponse(request)
