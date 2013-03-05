from django.core.management import setup_environ
import brainstormtg.settings
setup_environ(brainstormtg.settings)
from django.contrib.auth.models import User

if User.objects.count() == 0:
    admin = User.objects.create(username='admin')
    admin.set_password('admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
