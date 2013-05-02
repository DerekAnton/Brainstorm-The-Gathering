#!/usr/bin/env python

from django.core.management import setup_environ
import brainstormtg.settings
import os
from django.conf import settings
setup_environ(brainstormtg.settings)
settings.HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'
from django.db import models
from django.contrib.auth.models import User
import os
import brainstormtg.settings
from mainsite.models import Format, Archetype, PublishedDeck

Archetype.objects.all().delete()
standard = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					arc, new = Archetype.objects.get_or_create(colors=w+u+b+r+g, format='Standard')
					if new:
						arc.save()
					standard.append(arc) 
modern = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					arc, new = Archetype.objects.get_or_create(colors=w+u+b+r+g, format='Modern')
					if new:
						arc.save()
					modern.append(arc)
legacy = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					arc, new = Archetype.objects.get_or_create(colors=w+u+b+r+g, format='Legacy')
					if new:
						arc.save()
					legacy.append(arc)
vintage = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					arc, new = Archetype.objects.get_or_create(colors=w+u+b+r+g, format='Vintage')
					if new:
						arc.save()
					vintage.append(arc)
'''commander = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					commander.append(Archetype(colors=w+u+b+r+g, format='Commander'))'''
for deck in PublishedDeck.objects.filter(user=User.objects.filter(username='admin')[0]):
	print deck.name
	if not deck.standard_legal and 'standard' in deck.name:
		print 'standard'
		for archetype in standard:
			archetype.update(deck)
			archetype.save()
	elif not deck.modern_legal and 'modern' in deck.name:
		print 'modern'
		for archetype in modern:
			archetype.update(deck)
			archetype.save()
	elif not deck.legacy_legal and 'legacy' in deck.name:
		print 'legacy'
		for archetype in legacy:
			archetype.update(deck)
			archetype.save()
	elif not deck.vintage_legal and 'vintage' in deck.name:
		print 'vintage'
		for archetype in vintage:
			archetype.update(deck)
			archetype.save()
	'''elif deck.commander_legal:
		for archetype in commander:
			archetype.update(deck)'''
