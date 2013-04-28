from haystack import indexes
import datetime
from mainsite.models import Card, PublishedDeck
from django.contrib.auth.models import User

class CardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Card

    def index_queryset(self, using=None):
        return self.get_model().objects

class PublishedDeckIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return PublishedDeck

    def index_queryset(self, using=None):
        return self.get_model().objects

class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().objects
