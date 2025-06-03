from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home_view,
    register_view,
    area_personale_view,
    crea_pratica_view,
    dettaglio_pratica_view,
    area_notaio_view,
    area_geometra_view,
    crea_annuncio_ai_view,  # ✅ aggiunta
)

app_name = "real_estate"  # Namespace per usare {% url 'real_estate:nome' %}

urlpatterns = [
    # Homepage
    path('', home_view, name='home'),

    # Autenticazione
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='real_estate:home'), name='logout'),
    path('accounts/register/', register_view, name='register'),

    # Area utente e gestione pratiche
    path('area-personale/', area_personale_view, name='area_personale'),
    path('crea-pratica/', crea_pratica_view, name='crea_pratica'),
    path('pratica/<int:pratica_id>/', dettaglio_pratica_view, name='dettaglio_pratica'),

    # Aree specifiche per ruoli particolari
    path('area-notaio/', area_notaio_view, name='area_notaio'),
    path('area-geometra/', area_geometra_view, name='area_geometra'),

    # ✅ Nuova route per annuncio AI
    path('crea-annuncio-ai/<int:pratica_id>/', crea_annuncio_ai_view, name='crea_annuncio_ai'),
]
