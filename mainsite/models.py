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
