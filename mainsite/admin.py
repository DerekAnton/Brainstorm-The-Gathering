from django.contrib import admin
from mainsite.models import *

class CardAdmin(admin.ModelAdmin):
    filter_horizontal = ('sets','typing','super_typing','sub_typing')
admin.site.register(Card, CardAdmin)
admin.site.register(Typing)
admin.site.register(SuperTyping)
admin.site.register(SubTyping)
admin.site.register(Set)
admin.site.register(CardCount)
admin.site.register(Deck)
admin.site.register(PublishedDeck)
admin.site.register(Collection)
admin.site.register(Comment)
