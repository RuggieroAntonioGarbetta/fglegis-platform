from django.http import HttpResponse

def home(request):
    return HttpResponse("Benvenuto nella piattaforma documentale immobiliare FG LEGIS")
