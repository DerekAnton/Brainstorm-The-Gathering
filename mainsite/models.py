from django.db import models
from datetime import datetime, tzinfo, timedelta

from django.contrib.auth.models import User

class EST(tzinfo):

    def utcoffset(self, dt):
        return timedelta(hours=-5)

    def tzname(self, dt):
        return 'EST'

    def dst(self, dt):
        return timedelta(0)

class FavoriteCard(models.Model):
    card = models.ForeignKey('mainsite.Card')
    user = models.OneToOneField(User)

class Card(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    manacost = models.CharField(max_length=200, null=True)
    rules = models.TextField(null=True)
    power = models.CharField(max_length=200, null=True)
    toughness = models.CharField(max_length=200, null=True)
    sets = models.ManyToManyField('mainsite.Set')
    typing = models.ManyToManyField('mainsite.Typing')
    sub_typing = models.ManyToManyField('mainsite.SubTyping')
    super_typing = models.ManyToManyField('mainsite.SuperTyping')

    def urlName(self):
        return name.replace('/', '-').replace(',', '-').replace(' ', '_').replace('\'', '-')

    def __unicode__(self):
        return self.name

    def get_image_url(self, set_name):
        return "http://static.brainstormtg.com/card_images/%s/%s.jpeg" % (set_name, self.name)

    def get_absolute_url(self):
        return "/info/%s/%s/" % (self.sets.all()[0], self.name)

class Format(models.Model):
    name = models.CharField(max_length=200)
    legal_sets = models.ManyToManyField('mainsite.Set')
    banned_cards = models.ManyToManyField('mainsite.Card',related_name='banned_cards')
    restricted_cards = models.ManyToManyField('mainsite.Card',related_name='restricted_cards')

class Set(models.Model):
    name = models.CharField(max_length=200)
    long_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Typing(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class SubTyping(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class SuperTyping(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class CardCount(models.Model):
    card = models.ForeignKey('mainsite.Card')
    multiplicity = models.IntegerField()

    @staticmethod
    def getCardCount(_card,_multiplicity):
        if CardCount.objects.filter(card=_card).filter(multiplicity=_multiplicity).count() == 0:
            newCount = CardCount(card=_card,multiplicity=_multiplicity)
            newCount.save()
            return newCount
        else:
            return CardCount.objects.filter(card=_card).get(multiplicity=_multiplicity)

class Deck(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    created = models.DateTimeField('datetime.now(EST())')
    description = models.TextField()
    card_counts = models.ManyToManyField('mainsite.CardCount')

    def publish(self):
        publishedDeck = PublishedDeck(legacy_legal=self.format_check(Format.objects.get(name=legacy)),vintage_legal=self.format_check(Format.objects.get(name=vintage)),modern_legal=self.format_check(Format.objects.get(name=modern)),standard_legal=self.format_check(Format.objects.get(name=standard)),commander_legal=self.format_check(Format.objects.get(name=commander)),score=0,user=self.user,published=datetime.now(EST()),description=self.description,card_counts=self.card_counts.objects.all())
        publishedDeck.save()
        return publishedDeck

    def addCard(self, str):  #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
            num = self.card_counts.get(card=Card.objects.get(name=str)).multiplicity
            self.card_counts.remove(self.card_counts.get(card=Card.objects.get(name=str)))
            self.card_counts.add(CardCount.getCardCount(Card.objects.get(name=str),num+1))
        else:
            self.card_counts.add(CardCount.getCardCount(Card.objects.get(name=str),1))

    def removeCard(self, str): #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
            self.card_counts.get(card=Card.objects.get(name=str)).delete()

    def setNumCard(self, str, num):
        if (num <= 0):
            if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
                self.card_counts.get(card=Card.objects.get(name=str)).delete()
        else:
            if(self.card_counts.filter(card=Card.objects.get(name=str)).count() == 0):
                if (CardCount.objects.filter(card=Card.objects.get(name=str)).filter(multiplicity=num).count() == 0):
                    card = CardCount(card=Card.objects.get(name=str),multiplicity=num)
                    card.save()
                    self.card_counts.add(card)
                else:
                    self.card_counts.add(CardCount.objects.filter(card=Card.objects.get(name=str)).get(multiplicity=num))
            else:
                card = self.card_counts.get(card=Card.objects.get(name=str))
                card.multiplicity = num

    def format_check(self, format): #returns true if the calling deck is legal in format
        for _card_count in card_counts:
            if _card_count.card in format.banned_cards:
                return False
            if _card_count.card in format.restricted_cards and _card_count.multiplicity > 1:
                return False
            legal_sets = False
            for _set in _card_count.card.sets:
                if _set in format.legal_sets:
                    legal_sets = True
            if not legal_sets:
                return False
        return True

class PublishedDeck(models.Model):
    name = models.CharField(max_length=200)
    score = models.IntegerField()
    user = models.ForeignKey(User)
    published = models.DateTimeField()
    description = models.TextField()
    card_counts = models.ManyToManyField('mainsite.CardCount')
    legacy_legal = models.BooleanField()
    vintage_legal = models.BooleanField()
    modern_legal = models.BooleanField()
    standard_legal = models.BooleanField()
    commander_legal = models.BooleanField()

    def pull_deck(self, newUser):
        ownedDeck = Deck(user=newUser,created=datetime.now(EST()),description=self.description,card_counts=self.card_counts.objects.all())
        ownedDeck.save()
        return ownedDeck

    def increment_score(self):
        self.score = self.score + 1
        self.save()
        return self.score

    def decrement_score(self):
        self.score = self.score - 1
        self.save()
        return self.score

class Collection(models.Model):
    user = models.ForeignKey(User)
    cards = models.ManyToManyField('mainsite.Card')

    def addCard(self, str):  #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).count() == 0):
            if (CardCount.objects.filter(card=Card.objects.get(name=str)).filter(multiplicity=1).count() == 0):
                card = CardCount(card=Card.objects.get(name=str),multiplicity=1)
                card.save()
                self.card_counts.add(card)
            else:
                self.card_counts.add(CardCount.objects.filter(card=Card.objects.get(name=str)).get(multiplicity=1))
        else:
            card = self.card_counts.get(card=Card.objects.get(name=str))
            card.multiplicity = card.multiplicity + 1

    def removeCard(self, str): #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
            self.card_counts.get(card=Card.objects.get(name=str)).delete()

    def setNumCard(self, str, num):
        if (num <= 0):
            if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
                self.card_counts.get(card=Card.objects.get(name=str)).delete()
        else:
            if(self.card_counts.filter(card=Card.objects.get(name=str)).count() == 0):
                if (CardCount.objects.filter(card=Card.objects.get(name=str)).filter(multiplicity=num).count() == 0):
                    card = CardCount(card=Card.objects.get(name=str),multiplicity=num)
                    card.save()
                    self.card_counts.add(card)
                else:
                    self.card_counts.add(CardCount.objects.filter(card=Card.objects.get(name=str)).get(multiplicity=num))
            else:
                card = self.card_counts.get(card=Card.objects.get(name=str))
                card.multiplicity = num

class Comment(models.Model):
    user = models.ForeignKey(User)
    published_deck = models.ForeignKey('mainsite.PublishedDeck')
    timestamp = models.DateTimeField()
    message = models.TextField()
