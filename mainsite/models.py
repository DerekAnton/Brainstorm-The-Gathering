from django.db import models
import re
from datetime import datetime, tzinfo, timedelta
import unicodedata
from django.contrib.auth.models import User
from django.db import models
from haystack import signals

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
    cmc = models.IntegerField()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_image_url(self, set_name=None):
        if set_name and self.sets.all().filter(name=set_name):
            return "http://static.brainstormtg.com/card_images/%s/%s.jpeg" % (set_name,self.name)
        return "http://static.brainstormtg.com/card_images/%s/%s.jpeg" % (self.sets.all()[0],self.name)

    def get_absolute_url(self):
        return "/info/%s/%s/" % (self.sets.all()[0], self.name)

    def get_absolute_url(self, set_name=None):
        if set_name and self.sets.all().filter(name=set_name):
            return "/info/%s/%s/" % (self.sets.all().get(name=set_name),self.name)
        return "/info/%s/%s/" % (self.sets.all()[0], self.name)

class Format(models.Model):
    name = models.CharField(max_length=200)
    legal_sets = models.ManyToManyField('mainsite.Set')
    banned_cards = models.ManyToManyField('mainsite.Card',related_name='banned_cards')
    restricted_cards = models.ManyToManyField('mainsite.Card',related_name='restricted_cards')

    def __unicode__(self):
        return self.name

    def checkCard(self, card):
        for _set in self.legal_sets.all():
            if card.sets.filter(pk=_set.pk):
                if self.banned_cards.filter(pk=card.pk):
                    return 'Banned'
                if self.restricted_cards.filter(pk=card.pk):
                    return 'Restricted'
                return 'Legal'
        return 'Banned'

    def legal(self, deck):
        numCards = 0
        for card_count in deck.card_counts.all():
            numCards += card_count.multiplicity
            if self.checkCard(card_count.card) == 'Banned':
                return False
            if self.checkCard(card_count.card) == 'Restricted' and card_count.multiplicity > 1 and not card_count.card.super_typing.filter(name='Basic') and not card_count.card.name == 'Relentless Rats':
                return False
            if card_count.multiplicity > 4 and not card_count.card.super_typing.filter(name='Basic') and not card_count.card.name == 'Relentless Rats':
                return False
        if numCards < 60:
            return False
        if self.name == 'commander' and numCards != 100:
            return False
        numCards = 0
        for card_count in deck.sb_counts.all():
            numCards += card_count.multiplicity
            if self.checkCard(card_count.card) == 'Banned':
                return False
            if self.checkCard(card_count.card) == 'Restricted' and card_count.multiplicity > 1 and not card_count.card.super_typing.filter(name='Basic') and not card_count.card.name == 'Relentless Rats':
                return False
            if card_count.multiplicity > 4 and not card_count.card.super_typing.filter(name='Basic') and not card_count.card.name == 'Relentless Rats':
                return False
            if deck.card_counts.filter(card=card_count.card):
                if deck.card_counts.get(card=card_count.card).multiplicity + card_count.multiplicity > 4 and not card_count.card.super_typing.filter(name='Basic') and not card_count.card.name == 'Relentless Rats':
                    return False
                if self.checkCard(card_count.card) == 'Restricted' and deck.card_counts.get(card=card_count.card).multiplicity + card_count.multiplicity > 1 and not card_count.card.super_typing.filter(name='Basic') and not card_count.card.name == 'Relentless Rats':
                    return False
        if numCards == 0 or numCards == 15:
            return True
        return False

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
    card_counts = models.ManyToManyField('mainsite.CardCount',related_name='md')
    sb_counts = models.ManyToManyField('mainsite.CardCount',related_name='sb')

    def __unicode__(self):
        return self.name

    def publish(self):
        publishedDeck = PublishedDeck(legacy_legal=self.format_check(Format.objects.get(name=legacy)),vintage_legal=self.format_check(Format.objects.get(name=vintage)),modern_legal=self.format_check(Format.objects.get(name=modern)),standard_legal=self.format_check(Format.objects.get(name=standard)),commander_legal=self.format_check(Format.objects.get(name=commander)),score=0,user=self.user,published=datetime.now(EST()),description=self.description,card_counts=self.card_counts.objects.all())
        publishedDeck.save()
        breakdown = Card_Breakdown()
        breakdown.initialize(publishedDeck)
        breakdown.save()
        return publishedDeck

    def addCard(self, str):  #argument is the name of the card to add
        self.setNumCard(str=str,num=1)
        '''if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
            num = self.card_counts.get(card=Card.objects.get(name=str)).multiplicity
            self.card_counts.remove(self.card_counts.get(card=Card.objects.get(name=str)))
            self.card_counts.add(CardCount.getCardCount(Card.objects.get(name=str),num+1))
        else:
            self.card_counts.add(CardCount.getCardCount(Card.objects.get(name=str),1))'''

    def removeCard(self, str): #argument is the name of the card to add
        if(self.card_counts.filter(card=Card.objects.get(name=str)).count() != 0):
            self.card_counts.get(card=Card.objects.get(name=str)).delete()

    def setNumCard(self, str, num):
        self.removeCard(str)
        if num > 0:
            cardCount, created = CardCount.objects.get_or_create(card=Card.objects.get(name=str),multiplicity=num)
            self.card_counts.add(cardCount)
            '''if(self.card_counts.filter(card=Card.objects.get(name=str)).count() == 0):
                if (CardCount.objects.filter(card=Card.objects.get(name=str)).filter(multiplicity=num).count() == 0):
                    card = CardCount(card=Card.objects.get(name=str),multiplicity=num)
                    card.save()
                    self.card_counts.add(card)
                else:
                    self.card_counts.add(CardCount.objects.filter(card=Card.objects.get(name=str)).get(multiplicity=num))
            else:
                card = self.card_counts.get(card=Card.objects.get(name=str))
                card.multiplicity = num'''

    def getMultiplicity(self, str):
        return int(self.card_counts.filter(card=Card.objects.get(name=str)).count())

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
    card_counts = models.ManyToManyField('mainsite.CardCount',related_name='mdPub')
    sb_counts = models.ManyToManyField('mainsite.CardCount',related_name='sbPub')
    legacy_legal = models.BooleanField()
    vintage_legal = models.BooleanField()
    modern_legal = models.BooleanField()
    standard_legal = models.BooleanField()
    commander_legal = models.BooleanField()
    comments = models.ManyToManyField('mainsite.Comment')

    def __unicode__(self):
        return self.name

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
    user = models.ForeignKey(User, primary_key=True)
    card_counts = models.ManyToManyField('mainsite.CardCount')

    def getMultiplicity(self, str):
        return int(self.card_counts.filter(card=Card.objects.get(name=str)).count())

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

class Card_Breakdown(models.Model):
    #number of cards
    number_of_cards = models.IntegerField(default=0)
    #mana count
    
    #COLORS ARE BASED OFF A STRING
    red_mana = models.IntegerField(default=0)
    blue_mana = models.IntegerField(default=0)
    green_mana = models.IntegerField(default=0)
    black_mana = models.IntegerField(default=0)
    white_mana = models.IntegerField(default=0)
    colorless_mana = models.IntegerField(default=0)

    red = models.IntegerField(default=0)
    blue = models.IntegerField(default=0)
    green = models.IntegerField(default=0)
    black = models.IntegerField(default=0)
    white = models.IntegerField(default=0)
    colorless = models.IntegerField(default=0)


    #card count types
    creature_count = models.IntegerField(default=0)
    land_count = models.IntegerField(default=0)
    sorcery_count = models.IntegerField(default=0)
    instant_count = models.IntegerField(default=0)
    enchantment_count = models.IntegerField(default=0)
    artifact_count = models.IntegerField(default=0)
    planeswalker_count = models.IntegerField(default=0)

    #MAPPING FOR MANA_CURVE
    mana_curve = models.CommaSeparatedIntegerField(max_length=500, default='0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0')

    deck = models.ForeignKey('mainsite.PublishedDeck')
    #Sub_decks to add
    
    
    def initialize(self, deck):
        print self.mana_curve
        super(Card_Breakdown,self).__init__()
        self.number_of_cards=0
        self.red_mana = 0
        self.blue_mana = 0
        self.green_mana = 0
        self.black_mana = 0
        self.white_mana = 0
        self.colorless_mana = 0

        self.red = 0
        self.blue = 0
        self.green = 0
        self.black = 0
        self.white = 0
        self.colorless = 0

        tempWhite = 0
        tempBlue = 0
        tempBlack = 0
        tempRed = 0
        tempGreen = 0

        self.creature_count = 0
        self.land_count = 0
        self.sorcery_count = 0
        self.instant_count = 0
        self.enchantment_count = 0
        self.artifact_count = 0
        self.planeswalker_count = 0
        curve=[0 for index in xrange(19)]
        for x in deck.card_counts.all():
            curve[x.card.cmc%20] += x.multiplicity
            if x.card.manacost:
                normal=unicodedata.normalize('NFKD', x.card.manacost).encode('ascii','ignore')
            else:
                normal=''
            #determines the color of the card
            if x.card.manacost:
                for z in x.card.manacost:
                    if z == 'R':
                        self.red_mana += x.multiplicity
                    elif z== 'U':
                        self.blue_mana += x.multiplicity
                    elif z == 'G':
                        self.green_mana += x.multiplicity
                    elif z == 'B':
                        self.black_mana += x.multiplicity
                    elif z == 'W':
                        self.white_mana += x.multiplicity

            if re.sub('[^0123456789]','',normal):
                self.colorless_mana += int(re.sub('[^0123456789]','',normal))*x.multiplicity
            #find a way to help out Ai algorithm
            
            if x.card.manacost and '/' in x.card.manacost:
                if 'R' in normal:
                    tempRed += x.multiplicity
                if 'U' in normal:
                    tempBlue += x.multiplicity
                if 'G' in normal:
                    tempGreen += x.multiplicity
                if 'B' in normal:
                    tempBlack += x.multiplicity
                if 'W' in normal:
                    tempWhite += x.multiplicity
            else:
                if 'R' in normal:
                    self.red += x.multiplicity
                if 'U' in normal:
                    self.blue += x.multiplicity
                if 'G' in normal:
                    self.green += x.multiplicity
                if 'B' in normal:
                    self.black += x.multiplicity
                if 'W' in normal:
                    self.white += x.multiplicity
                if not ('W' in normal or 'U' in normal or 'B' in normal or 'R' in normal or 'G' in normal):
                    self.colorless += x.multiplicity
            #determines the manacurve of card

            #determines the numbers of types
            
            if x.card.typing.filter(name='Sorcery'):
                self.sorcery_count += x.multiplicity
            if x.card.typing.filter(name='Creature'):
                self.creature_count += x.multiplicity
            if x.card.typing.filter(name='Land'):
                self.land_count += x.multiplicity
            if x.card.typing.filter(name='Instant'):
                self.instant_count += x.multiplicity
            if x.card.typing.filter(name='Artifact'):
                self.artifact_count += x.multiplicity
            if x.card.typing.filter(name='Enchantment'):
                self.enchantment_count += x.multiplicity
            if x.card.typing.filter(name='Planeswalker'):
                self.planeswalker_count += x.multiplicity

            self.number_of_cards += x.multiplicity

        if self.white:
            self.white += tempWhite
        if self.blue:
            self.blue += tempBlue
        if self.black:
            self.black += tempBlack
        if self.red:
            self.red += tempRed
        if self.green:
            self.green += tempGreen
        self.colorless -= self.land_count
        curve[0] -= self.land_count
        #get number of cards
        self.mana_curve=str(curve).strip('[]')
        print self.mana_curve
        self.deck=deck;

'''class Recommendation(models.Model):
    colors = models.CharField()
    curve = models.CommaSeparatedIntegerField(max_length=1000, default='0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0')
    cardsPk = models.CommaSeparatedIntegerField(max_length=500, default='0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0')
    basicLands = models.CommaSeparatedIntegerField(max_length=500, default='0, 0, 0, 0, 0')
    numDecks = models.IntegerField(default=0)
    count0 = models.ManyToManyField('mainsite.CardCount')
    count1 = models.ManyToManyField('mainsite.CardCount')
    count2 = models.ManyToManyField('mainsite.CardCount')
    count3 = models.ManyToManyField('mainsite.CardCount')
    count4 = models.ManyToManyField('mainsite.CardCount')
    count5 = models.ManyToManyField('mainsite.CardCount')
    count6 = models.ManyToManyField('mainsite.CardCount')
    count7 = models.ManyToManyField('mainsite.CardCount')
    count8 = models.ManyToManyField('mainsite.CardCount')
    count9 = models.ManyToManyField('mainsite.CardCount')
    count10 = models.ManyToManyField('mainsite.CardCount')
    count11 = models.ManyToManyField('mainsite.CardCount')
    count12 = models.ManyToManyField('mainsite.CardCount')
    count13 = models.ManyToManyField('mainsite.CardCount')
    count14 = models.ManyToManyField('mainsite.CardCount')
    count15 = models.ManyToManyField('mainsite.CardCount')
    count16 = models.ManyToManyField('mainsite.CardCount')
    count17 = models.ManyToManyField('mainsite.CardCount')
    count18 = models.ManyToManyField('mainsite.CardCount')

    def update(self, deck):
        breakdown = Card_Breakdown()
        breakdown.save()
        breakdown.initialize(deck)
        breakdown.save()
        self.numDecks += 1
        newCurve = list(breakdown.curve)
        curve = list(self.curve)
        for i in xrange(len(newCurve)):
            curve[i] += newCurve[i]
        self.curve = str(curve).strip('[]')
        for card_count in deck:
            if 
            cost = card_count.card.cmc
            count = None
            if cmc == 0:
                count = self.count0
            if cmc == 1:
                count = self.count1
            if cmc == 2:
                count = self.count2
            if cmc == 3:
                count = self.count3
            if cmc == 4:
                count = self.count4
            if cmc == 5:
                count = self.count5
            if cmc == 6:
                count = self.count6
            if cmc == 7:
                count = self.count7
            if cmc == 8:
                count = self.count8
            if cmc == 9:
                count = self.count9
            if cmc == 10:
                count = self.count10
            if cmc == 11:
                count = self.count11
            if cmc == 12:
                count = self.count12
            if cmc == 13:
                count = self.count13
            if cmc == 14:
                count = self.count14
            if cmc == 15:
                count = self.count15
            if cmc == 16:
                count = self.count16
            if cmc == 17:
                count = self.count17
            if cmc == 18:
                count = self.count18
            exists = False
            for _count in count:
                if _count.card.pk == card_count.card.pk:
                    exists = True
                    _count.multiplicity += card_count.multiplicity
                if not exists:
            if not exitst:
                count.add(CardCount(card=card_count))'''

class DynamicIndexSignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        models.signals.post_save.connect(self.handle_save, sender=PublishedDeck)
        models.signals.post_delete.connect(self.handle_delete, sender=PublishedDeck)
        models.signals.post_save.connect(self.handle_save, sender=User)
        models.signals.post_delete.connect(self.handle_delete, sender=User)

    def teardown(self):
        models.signals.post_save.disconnect(self.handle_save, sender=PublishedDeck)
        models.signals.post_delete.disconnect(self.handle_delete, sender=PublishedDeck)
        models.signals.post_save.disconnect(self.handle_save, sender=User)
        models.signals.post_delete.disconnect(self.handle_delete, sender=User)
