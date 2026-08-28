from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
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
