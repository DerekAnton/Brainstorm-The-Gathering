#!/usr/bin/env python

from django.core.management import setup_environ
import os
import brainstormtg.settings
setup_environ(brainstormtg.settings)
from mainsite.models import Card, Set, Typing, SubTyping, SuperTyping, Format

import xml.etree.ElementTree as ET

import requests
import os

tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'formats.xml'))
legacy = tree.find('legacy')
vintage = tree.find('vintage')
modern = tree.find('modern')
standard = tree.find('standard')
commander = tree.find('commander')
formats = [legacy, vintage, modern, standard, commander]

for _format in formats:
    newFormat = Format(name=_format.find('format_name').text)
    newFormat.save()
    if _format.find('sets').find('set').find('name').text == 'all':
        for _set in Set.objects.all():
            newFormat.legal_sets.add(Set.objects.get(name=_set.name))
    else:
        for _set in _format.find('sets').findall('set'):
            newFormat.legal_sets.add(Set.objects.get(long_name=_set.find('name').text))
    newFormat.save()
    for _card in _format.find('banned').findall('card'):
    	print _card.find('name').text
        newFormat.banned_cards.add(Card.objects.get(name=_card.find('name').text))
    newFormat.save()
    if len(_format.find('restricted')) and _format.find('restricted').find('card').find('name').text == 'singleton':
        for _card in Card.objects.all():
            newFormat.restricted_cards.add(Card.objects.get(name=_card.name))
    else:
        for _card in _format.find('restricted').findall('card'):
        	print _card.find('name').text
        	newFormat.restricted_cards.add(Card.objects.get(name=_card.find('name').text))
    newFormat.save();