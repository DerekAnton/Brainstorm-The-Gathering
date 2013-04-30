#!/usr/bin/env python
from django.core.management import setup_environ
import os
import brainstormtg.settings
setup_environ(brainstormtg.settings)
settings.HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'
from mainsite.models import Card, PublishedDeck, CardCount, Card_Breakdown
from django.contrib.auth.models import User

import requests
from bs4 import BeautifulSoup
import re

from haystack.query import SearchQuerySet

from datetime import datetime

r = requests.get("http://www.starcitygames.com/pages/decklists/")
soup = BeautifulSoup(r.text)

top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']

table = BeautifulSoup(requests.get(top).text).find('section', id="content").table

deck_links = [r.find('td').find('a')['href'] for r in table.findAll('tr')[5:]]

match = re.compile('^(\d+) ((.)+)')
user = User.objects.get(username='admin')

for deck_link in deck_links[:8]:
    r = requests.get(deck_link)
    soup = BeautifulSoup(r.text)
    title = soup.find('header', {'class':'deck_title'}).a.text
    print(title)
    try:
        PublishedDeck.objects.get(name=title)
        print("\tAlready Created")
    except:
        pass
    deck = PublishedDeck(name=title,published=datetime.now(),score=0,user=user)
    deck.save()
    wrapper = soup.find('div', {'class': 'deck_card_wrapper'})
    matches = [match.search(li.text) for li in wrapper.findAll('li')]
    card_counts = {m.group(2):m.group(1) for m in matches if m}
    for card_count in card_counts:
        card = Card.objects.get(name=card_count)
        print "\t%s (%s) x %s" % (card, card_count, card_counts[card_count])
        count = CardCount(card=card, multiplicity=int(card_counts[card_count]))
        count.save()
        deck.card_counts.add(count)
    breakdown = Card_Breakdown()
    breakdown.initialize(deck)
    breakdown.save()
