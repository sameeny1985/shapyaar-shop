from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added


def make_admin_if_needed(user):
    if user.email and user.email.lower() == settings.ADMIN_EMAIL.lower():
        user.is_staff = True
        user.is_superuser = True
        user.save()


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    make_admin_if_needed(user)


@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    make_admin_if_needed(sociallogin.user)


@receiver(post_save, sender=User)
def on_user_save(sender, instance, created, **kwargs):
    if created:
        make_admin_if_needed(instance)
