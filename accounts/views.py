from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
@require_GET
def make_admin(request):
    secret = request.GET.get('key')
    if secret != 'shopyaar-make-admin-2026':
        return HttpResponse('Invalid key', status=403)
    
    try:
        user = User.objects.get(email__iexact='shapyaar@gmail.com')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return HttpResponse(f'SUCCESS! {user.email} is now staff={user.is_staff} superuser={user.is_superuser}. You can delete this URL later.')
    except User.DoesNotExist:
        return HttpResponse('User shapyaar@gmail.com not found. Login with Google first, then try again.')

@require_GET
def fix_empty_usernames(request):
    key = request.GET.get('key', '')
    if key != 'lylox-fix-user-2026':
        return HttpResponse('Forbidden', status=403)

    User = get_user_model()
    fixed = []
    for user in User.objects.all():
        if not user.username:
            base = (user.email or f'user{user.pk}').split('@')[0][:120] or f'user{user.pk}'
            candidate = base
            n = 0
            while User.objects.filter(username=candidate).exclude(pk=user.pk).exists():
                n += 1
                candidate = f'{base}{n}'
            user.username = candidate
            # اگر ادمین است staff بماند
            if user.email and user.email.lower() == 'shapyaar@gmail.com':
                user.is_staff = True
                user.is_superuser = True
            user.save()
            fixed.append(f'{user.email} -> {user.username}')

    if not fixed:
        return HttpResponse('OK: no empty usernames found')
    return HttpResponse('FIXED:\n' + '\n'.join(fixed), content_type='text/plain')
