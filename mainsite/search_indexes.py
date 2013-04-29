from haystack import indexes
import datetime
from mainsite.models import Card, PublishedDeck
from django.contrib.auth.models import User

class CardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    color = indexes.CharField(use_template=True)
    power = indexes.CharField(model_attr='power', faceted=True)
    toughness = indexes.CharField(model_attr='toughness', faceted=True)
    cmc = indexes.CharField(model_attr='cmc', faceted=True)

    sets = indexes.MultiValueField()
    types = indexes.MultiValueField()
    subs = indexes.MultiValueField()
    supers = indexes.MultiValueField()

    def get_model(self):
        return Card

    def index_queryset(self, using=None):
        return self.get_model().objects

    def prepare_sets(self, obj):
        return [(s.name) for s in obj.sets.all()]

    def prepare_types(self, obj):
        return [(s.name) for s in obj.typing.all()]

    def prepare_subs(self, obj):
        return [(s.name) for s in obj.sub_typing.all()]

    def prepare_supers(self, obj):
        return [(s.name) for s in obj.super_typing.all()]

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
