from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

TIPO_PRATICA_CHOICES = [
    ('preliminare', 'Preliminare'),
    ('rogito', 'Rogito'),
    ('visura', 'Visura'),
    ('catastale', 'Catastale'),
    ('altro', 'Altro'),
]

class PraticaImmobiliare(models.Model):
    nome_azienda = models.CharField(max_length=255)
    tipo_pratica = models.CharField(
        max_length=50,
        choices=TIPO_PRATICA_CHOICES,
        verbose_name="Tipo di pratica"
    )
    tipo_personalizzato = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Altro tipo (se specificato)"
    )
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pratiche_utente")
    notaio = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pratiche_notaio")
    geometra = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pratiche_geometra")
    note = models.TextField(blank=True, null=True, verbose_name="Note interne / comunicazioni")
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_scadenza = models.DateField(null=True, blank=True, verbose_name="Data di scadenza")
    completata = models.BooleanField(default=False)
    firma_digitale = models.BooleanField(default=False)

    # ✅ Dati VENDITORE
    venditore_nome = models.CharField(max_length=100, blank=True)
    venditore_cognome = models.CharField(max_length=100, blank=True)
    venditore_indirizzo = models.CharField(max_length=255, blank=True)
    venditore_email = models.EmailField(blank=True)
    venditore_cellulare = models.CharField(max_length=20, blank=True)

    # ✅ Dati ACQUIRENTE
    acquirente_nome = models.CharField(max_length=100, blank=True)
    acquirente_cognome = models.CharField(max_length=100, blank=True)
    acquirente_email = models.EmailField(blank=True)
    acquirente_cellulare = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-data_creazione']
        verbose_name = "Pratica Immobiliare"
        verbose_name_plural = "Pratiche Immobiliari"

    def __str__(self):
        tipo = self.get_tipo_pratica_display() if self.tipo_pratica != 'altro' else self.tipo_personalizzato
        return f"{self.nome_azienda} – {tipo}"


class Documento(models.Model):
    pratica = models.ForeignKey(PraticaImmobiliare, on_delete=models.CASCADE, related_name='documenti')
    nome = models.CharField(max_length=255)
    file = models.FileField(upload_to='documenti_pratiche/', null=True, blank=True)
    caricato_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-caricato_il']
        verbose_name = "Documento"
        verbose_name_plural = "Documenti"

    def __str__(self):
        return self.nome


class NotaPratica(models.Model):
    pratica = models.ForeignKey(PraticaImmobiliare, on_delete=models.CASCADE, related_name='note_pratica')
    autore = models.ForeignKey(User, on_delete=models.CASCADE)
    testo = models.TextField()
    risposta_a = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='risposte')
    data_creazione = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_creazione']
        verbose_name = "Nota"
        verbose_name_plural = "Note"

    def __str__(self):
        return f"Nota di {self.autore.username} – {self.data_creazione.strftime('%d/%m/%Y %H:%M')}"


class LogAttivitaPratica(models.Model):
    pratica = models.ForeignKey(PraticaImmobiliare, on_delete=models.CASCADE, related_name='log_attivita')
    utente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    azione = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log attività"
        verbose_name_plural = "Log attività"

    def __str__(self):
        return f"{self.timestamp.strftime('%d/%m/%Y %H:%M')} – {self.utente.username if self.utente else 'Sistema'} – {self.azione}"

RUOLI = [
    ('admin', 'Admin'),
    ('titolare_agenzia', 'Titolare Agenzia'),
    ('store_manager', 'Store Manager'),
    ('agente', 'Agente'),
    ('notaio', 'Notaio'),
    ('geometra', 'Geometra'),
]


class ProfiloUtente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ruolo = models.CharField(max_length=20, choices=RUOLI)
    filiale = models.CharField(max_length=100, blank=True, null=True)

    titolare = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titolare_utenti',
        help_text='Solo per store manager e agenti: titolare del gruppo'
    )
    store_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_manager_utenti',
        help_text='Solo per agenti: store manager di riferimento'
    )

    logo = models.ImageField(upload_to='loghi_utente/', null=True, blank=True)
    sito_web = models.URLField(blank=True, null=True)

    in_fase_di_registrazione = models.BooleanField(default=True)

    def __str__(self):
        stato = "In registrazione" if self.in_fase_di_registrazione else "Attivo"
        return f"{self.user.username} – {self.ruolo} – {stato}"


@receiver(post_save, sender=User)
def crea_profilo_utente(sender, instance, created, **kwargs):
    if created:
        ProfiloUtente.objects.create(user=instance)


# ✅ MODELLO ANNUNCIO AI
class AnnuncioAI(models.Model):
    TIPOLOGIA = [
        ('foto', 'Carica Foto'),
        ('video', 'Carica Video'),
    ]

    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    pratica = models.ForeignKey(PraticaImmobiliare, on_delete=models.CASCADE, related_name="annunci_ai")
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    tipologia = models.CharField(max_length=10, choices=TIPOLOGIA)
    immagini = models.FileField(upload_to='annunci/immagini/', blank=True, null=True)
    video = models.FileField(upload_to='annunci/video/', blank=True, null=True)
    creato_il = models.DateTimeField(auto_now_add=True)
    elaborato = models.BooleanField(default=False)
    video_generato = models.FileField(upload_to='annunci/finali/', blank=True, null=True)
    testo_generato = models.TextField(blank=True)

    class Meta:
        verbose_name = "Annuncio AI"
        verbose_name_plural = "Annunci AI"

    def __str__(self):
        return f"Annuncio di {self.utente.username} – {self.titolo}"
