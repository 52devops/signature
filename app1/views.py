from django.http import HttpResponse
from signature.sign import Signer


@Signer()
def get_app(request):
    return HttpResponse('ok', status=200)
