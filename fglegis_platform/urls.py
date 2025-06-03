from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from real_estate import views  # Importa views di real_estate

urlpatterns = [
    path('', views.home_view, name='home'),  # Homepage
    path('admin/', admin.site.urls),

    # Rotte per autenticazione (login/logout)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Includi tutte le altre rotte di real_estate (esclusi login/logout)
    path('', include('real_estate.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
