from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Address


@receiver(post_save, sender=User)
def create_address(sender, instance, created, **kwargs):

    if created:
        Address.objects.create(user=instance)
        print('Address created!')
