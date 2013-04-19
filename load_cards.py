#!/usr/bin/env python
import re
from django.core.management import setup_environ
import os
import brainstormtg.settings
setup_environ(brainstormtg.settings)
from mainsite.models import Card, Set, Typing, SubTyping, SuperTyping, Format

import xml.etree.ElementTree as ET
tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cards.xml'))
sets = tree.find('sets').findall('set')
cards = tree.find('cards').findall('card')

import requests
import os

print("Loading Cards into database... this will take a while...")

for _set in sets:
    name = _set.find('name').text
    if Set.objects.filter(name=name):
        continue
    long_name = _set.find('longname').text
    new_set = Set(name=name, long_name=long_name)
    new_set.save()
    """if not os.path.exists('images/%s' % name):
        os.makedirs('images/%s' % name)"""

types = set(['Artifact', 'Creature', 'Enchantment', 'Instant', 'Land', 'Planeswalker', 'Sorcery', 'Tribal'])
super_types = set(['Basic', 'Legendary', 'Snow', 'World'])
for card in cards:
    name = card.find('name').text.replace('/', '-')
    print name
    if Card.objects.filter(name=name):
        continue
    try:
        power, toughness = card.find('pt').text.replace('{1/2}', '.5').split('/')
    except AttributeError:
        power, toughness = '', ''
    try:
        color = card.find('color').text
    except AttributeError:
        color = ''
    try:
        try:
            left, right = card.find('type').text.split(' - ')
        except ValueError:
            left, right = [card.find('type').text], []
        typing = set(left.split(' ')).intersection(types)
        super_typing = set(left.split(' ')).intersection(super_types)
        sub_typing = right.split(' ')
    except AttributeError:
        typing = []
        super_typing = []
        sub_typing = []
    try:
        rules = card.find('text').text.encode('ascii', 'ignore')
    except AttributeError:
        rules = ''
    manacost = card.find('manacost').text
    #print manacost
    counter = 0
    colorless = 0
    cmc = manacost
    if not cmc:
        cmc = ""
    cmc=re.sub(r'\(2/','w',cmc)
    cmc=re.sub('[^0123456789wubrgWUBRG/]','',cmc)
    #print cmc
    for c in cmc:
        if c in 'wubrgWUBRG':
            counter += 1
        elif c in '0123456789':
            colorless += 1
        elif c == '/':
            counter = counter - 1;
    if colorless != 0:
        counter += int(cmc[:colorless])
    #print counter
    new_card = Card(name=name,color=color,manacost=manacost,rules=rules,power=power,toughness=toughness,cmc=counter)
    new_card.save()
    for s in card.findall('set'):
        _set = s.text
        '''if not os.path.exists('images/%s/%s.jpeg' % (_set, name)):
            r = requests.get(s.get('picURL'))
            with open('images/%s/%s.jpeg' % (_set, name), 'wb') as image:
                image.write(r.content)'''
        new_card.sets.add(Set.objects.get(name=_set))
    for t in typing:
        new_card.typing.add(Typing.objects.get_or_create(name=t)[0])
    for s in super_typing:
        new_card.super_typing.add(SuperTyping.objects.get_or_create(name=s)[0])
    for s in sub_typing:
        new_card.sub_typing.add(SubTyping.objects.get_or_create(name=s)[0])