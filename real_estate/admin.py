from django.contrib import admin
from .models import (
    PraticaImmobiliare,
    Documento,
    ProfiloUtente,
    NotaPratica,
    LogAttivitaPratica,
    AnnuncioAI,
)


@admin.register(PraticaImmobiliare)
class PraticaImmobiliareAdmin(admin.ModelAdmin):
    list_display = (
        'nome_azienda', 'tipo_pratica', 'utente',
        'notaio', 'geometra', 'data_creazione', 'completata'
    )
    list_filter = ('tipo_pratica', 'completata', 'data_creazione')
    search_fields = ('nome_azienda', 'utente__username')
    date_hierarchy = 'data_creazione'
    ordering = ('-data_creazione',)


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pratica', 'caricato_il')
    list_filter = ('caricato_il',)
    search_fields = ('nome',)
    date_hierarchy = 'caricato_il'
    ordering = ('-caricato_il',)


@admin.register(ProfiloUtente)
class ProfiloUtenteAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'ruolo', 'filiale',
        'titolare', 'store_manager', 'in_fase_di_registrazione'
    )
    list_filter = ('ruolo', 'in_fase_di_registrazione', 'filiale')
    search_fields = (
        'user__username', 'filiale',
        'titolare__username', 'store_manager__username'
    )
    ordering = ('user__username',)


@admin.register(NotaPratica)
class NotaPraticaAdmin(admin.ModelAdmin):
    list_display = ('pratica', 'autore', 'data_creazione', 'testo')
    list_filter = ('data_creazione',)
    search_fields = ('testo', 'autore__username')
    ordering = ('-data_creazione',)


@admin.register(LogAttivitaPratica)
class LogAttivitaPraticaAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'utente', 'pratica', 'azione')
    list_filter = ('timestamp',)
    search_fields = ('azione', 'utente__username')
    ordering = ('-timestamp',)


@admin.register(AnnuncioAI)
class AnnuncioAIAdmin(admin.ModelAdmin):
    list_display = ('pratica', 'titolo', 'tipologia', 'creato_il', 'elaborato')  # ✅ campo corretto
    list_filter = ('tipologia', 'elaborato', 'creato_il')  # ✅ corretto
    search_fields = ('titolo', 'pratica__nome_azienda')
    date_hierarchy = 'creato_il'
    ordering = ('-creato_il',)
