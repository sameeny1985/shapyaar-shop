from django.conf import settings
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_added
from allauth.account.signals import user_signed_up


ADMIN_EMAIL = getattr(settings, 'ADMIN_EMAIL', 'shapyaar@gmail.com').lower().strip()


def _ensure_username(user):
    """اگر username خالی است، از ایمیل بساز تا unique constraint نشکند."""
    if user.username:
        return
    base = (user.email or 'user').split('@')[0][:120] or 'user'
    candidate = base
    # اگر تکراری بود یک پسوند ساده بگذار
    from django.contrib.auth import get_user_model
    User = get_user_model()
    n = 0
    while User.objects.filter(username=candidate).exclude(pk=user.pk).exists():
        n += 1
        candidate = f"{base}{n}"
    user.username = candidate


def make_admin_if_needed(user):
    if not user or not getattr(user, 'email', None):
        return

    email = user.email.lower().strip()
    if email != ADMIN_EMAIL:
        return

    _ensure_username(user)

    user.is_staff = True
    user.is_superuser = True

    # فقط اگر کاربر قبلاً در دیتابیس ذخیره شده، save کن
    if user.pk:
        user.save(update_fields=['username', 'is_staff', 'is_superuser'])


@receiver(pre_social_login)
def on_pre_social_login(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if not user:
        return
    _ensure_username(user)
    # روی کاربر ذخیره‌نشده save نکن؛ فقط فلگ‌ها را ست کن
    if user.email and user.email.lower().strip() == ADMIN_EMAIL:
        user.is_staff = True
        user.is_superuser = True
    if user.pk:
        make_admin_if_needed(user)


@receiver(user_signed_up)
def on_user_signed_up(sender, request, user, **kwargs):
    _ensure_username(user)
    make_admin_if_needed(user)
    if user.pk and not user.username:
        user.save(update_fields=['username'])


@receiver(social_account_added)
def on_social_account_added(sender, request, sociallogin, **kwargs):
    make_admin_if_needed(sociallogin.user)
