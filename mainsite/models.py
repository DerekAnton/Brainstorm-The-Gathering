from django.db import models

from django.contrib.auth.models import User

class Card(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    manacost = models.CharField(max_length=200, null=True)
    flavor = models.TextField(null=True)
    power = models.CharField(max_length=200, null=True)
    toughness = models.CharField(max_length=200, null=True)
    sets = models.ManyToManyField('mainsite.Set')
    typing = models.ManyToManyField('mainsite.Typing')
    sub_typing = models.ManyToManyField('mainsite.SubTyping')
    super_typing = models.ManyToManyField('mainsite.SuperTyping')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/info/%s/%s/" % (self.sets.all()[0], self.name)

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

class Deck(models.Model):
    user = models.ForeignKey(User)
    created = models.BooleanField()
    description = models.TextField()
    card_counts = models.ManyToManyField('mainsite.CardCount')
    def addCard(self, str):  #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).len() == 0):
            if (CardCount.objects.filter(card=Card.objects.get(name=str)).filter(multiplicity=1).len() == 0):
                card = CardCount(card=Card.objects.get(name=str),multiplicity=1)
                card.save()
                self.card_counts.add(card)
            else:
                self.card_counts.add(CardCount.objects.filter(card=Card.objects.get(name=str)).get(multiplicity=1))
        else:
            card = self.card_counts.get(card=Card.objects.get(name=str))
            card.multiplicity = card.multiplicity + 1
    def removeCard(self, str): #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).len() != 0):
            self.card_counts.get(card=Card.objects.get(name=str)).delete()
    def setNumCard(self, str, num):
        if (num <= 0):
            if(self.card_counts.filter(card=Card.objects.get(name=str)).len() != 0):
                self.card_counts.get(card=Card.objects.get(name=str)).delete()
        else:
            if(self.card_counts.filter(card=Card.objects.get(name=str)).len() == 0):
                if (CardCount.objects.filter(card=Card.objects.get(name=str)).filter(multiplicity=num).len() == 0):
                    card = CardCount(card=Card.objects.get(name=str),multiplicity=num)
                    card.save()
                    self.card_counts.add(card)
                else:
                    self.card_counts.add(CardCount.objects.filter(card=Card.objects.get(name=str)).get(multiplicity=num))
            else:
                card = self.card_counts.get(card=Card.objects.get(name=str))
                card.multiplicity = num

class PublishedDeck(models.Model):
    user = models.ForeignKey(User)
    published = models.BooleanField()
    description = models.TextField()
    card_counts = models.ManyToManyField('mainsite.CardCount')

class Collection(models.Model):
    user = models.ForeignKey(User)
    cards = models.ManyToManyField('mainsite.Card')

class Comment(models.Model):
    user = models.ForeignKey(User)
    published_deck = models.ForeignKey('mainsite.PublishedDeck')
    timestamp = models.DateTimeField()
    message = models.TextField()
