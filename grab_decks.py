#!/usr/bin/env python
from django.core.management import setup_environ
import os
import unicodedata
import brainstormtg.settings
from django.conf import settings
setup_environ(brainstormtg.settings)
settings.HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'
from mainsite.models import Card, PublishedDeck, CardCount, Card_Breakdown, Format
from django.contrib.auth.models import User

import requests
from bs4 import BeautifulSoup
import re

from haystack.query import SearchQuerySet

from datetime import datetime

r = requests.get("http://www.starcitygames.com/pages/decklists/")
soup = BeautifulSoup(r.text)
user = User.objects.get(username='admin')

for format in ['standard', 'legacy', 'modern', 'vintage']:
    top = soup.find('div', id="dynamicpage_"+format+"_list").findAll('p')[0].a['href']
    top = unicodedata.normalize('NFKD', top).encode('ascii','ignore')
    table = BeautifulSoup(requests.get(top.replace('\r\n','')).text).find('section', id="content").table

    deck_links = [r.find('td').find('a')['href'] for r in table.findAll('tr')[5:]]

    match = re.compile('^(\d+) ((.)+)')

    for deck_link in deck_links[:8]:
        r = requests.get(deck_link)
        soup2 = BeautifulSoup(r.text)
        title = soup2.find('header', {'class':'deck_title'}).a.text
        print(title)
        try:
            PublishedDeck.objects.get(name=title)
            print("\tAlready Created")
        except:
            pass
        deck = PublishedDeck(name=title,published=datetime.now(),score=0,user=user)
        deck.save()
        wrapper = soup2.find('div', {'class': 'deck_card_wrapper'})
        matches = [match.search(li.text) for li in wrapper.findAll('li')]
        card_counts = {m.group(2):m.group(1) for m in matches if m}
        for card_count in card_counts:
            card = SearchQuerySet().models(Card).filter(content=card_count)[0].object
            print "\t%s (%s) x %s" % (card, card_count, card_counts[card_count])
            count = CardCount(card=card, multiplicity=int(card_counts[card_count]))
            count.save()
            deck.card_counts.add(count)
        breakdown = Card_Breakdown()
        breakdown.initialize(deck)
        breakdown.save()
        standard = Format.objects.filter(name='standard')[0]
        modern = Format.objects.filter(name='modern')[0]
        legacy = Format.objects.filter(name='legacy')[0]
        vintage = Format.objects.filter(name='vintage')[0]
        commander = Format.objects.filter(name='commander')[0]
        deck.standard_legal = standard.legal(deck)
        deck.modern_legal = modern.legal(deck)
        deck.legacy_legal = legacy.legal(deck)
        deck.vintage_legal = vintage.legal(deck)
        deck.commander_legal = commander.legal(deck)
        deck.save()