from django.utils import unittest
from mainsite.models import *
from datetime import datetime, tzinfo, timedelta
import django.test

from django.contrib.auth.models import User

class EST(tzinfo):

    def utcoffset(self, dt):
        return timedelta(hours=-5)

    def tzname(self, dt):
        return 'EST'

    def dst(self, dt):
        return timedelta(0)

class DeckModel(django.test.TestCase):
#NEED HELP SETTING THIS PART UP THE REST IS CORRECT

    def setUp(self):
        self.user = User(username='bob',password='pw')
        self.user.save()
        self.deck = Deck(created = datetime.now(EST()), description = ' deck ',user=self.user)
        self.deck.save()
        self.card = Card(name='Stone Giant',color='r',manacost='2rr',rules='',power=3,toughness=3)
        self.card.save()

    #TEST1 ADDING CARD
    def test_add_card(self):
        self.deck.addCard('Stone Giant')
        self.assertEqual(self.card,self.deck.card_counts.get(card=self.card).card)

    #TEST2 REMOVING CARD
    def test_remove_card(self):
        self.deck.addCard('Stone Giant')
        self.deck.removeCard('Stone Giant')
        self.assertEqual(self.deck.card_counts.count(),0)
        
    #TEST3 ADDING MULTIPLE OF THE SAME CARD Via ADD
    def test_multiplicty_from_adding(self):
        self.deck.addCard('Stone Giant')
        self.deck.addCard('Stone Giant')
        self.assertEqual(self.deck.card_counts.get(card=self.card).multiplicity, 2)
        
    #TEST4 USING SETNUM METHOD
    def test_setNumCard(self):
        self.deck.setNumCard('Stone Giant', 21)
        self.assertEqual(self.deck.card_counts.get(card=self.card).multiplicity, 21)
        
    #TEST5 USING SETNUMCARD TO REMOVE CARDS
    def test_setNumCard_removal(self):
        self.deck.setNumCard('Stone Giant',69)
        self.deck.setNumCard('Stone Giant', 0)
        self.assertEqual(self.deck.card_counts.count(),0)