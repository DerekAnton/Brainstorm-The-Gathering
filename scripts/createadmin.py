#!/usr/bin/env python

from django.contrib.auth.models import User
from mainsite.models import Collection
if User.objects.count() == 0:
    admin = User.objects.create(username='admin')
    admin.set_password('admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
    coll=Collection(user=admin)
    coll.save()
