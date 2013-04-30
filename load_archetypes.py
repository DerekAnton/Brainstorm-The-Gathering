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

standard = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					standard.append(Archetype(colors=w+u+b+r+g, format='Standard')) 
modern = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					modern.append(Archetype(colors=w+u+b+r+g, format='Modern'))
legacy = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					legacy.append(Archetype(colors=w+u+b+r+g, format='Legacy'))
vintage = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					vintage.append(Archetype(colors=w+u+b+r+g, format='Vintage'))
commander = []
for w in ['', 'W']:
	for u in ['', 'U']:
		for b in ['', 'B']:
			for r in ['', 'R']:
				for g in ['', 'G']:
					commander.append(Archetype(colors=w+u+b+r+g, format='Commander'))
for deck in PublishedDeck.objects.filter(user=User.objects.filter(username=admin)[0]):
	if deck.standard_legal:
		for archetype in standard:
			archetype.update(deck)
	elif deck.modern_legal:
		for archetype in modern:
			archetype.update(deck)
	elif deck.legacy_legal:
		for archetype in legacy:
			archetype.update(deck)
	elif deck.vintage_legal:
		for archetype in vintage:
			archetype.update(deck)
	elif deck.commander_legal:
		for archetype in commander:
			archetype.update(deck)
