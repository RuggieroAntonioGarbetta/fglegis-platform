from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import requests
from bs4 import BeautifulSoup

from .models import (
    PraticaImmobiliare,
    Documento,
    ProfiloUtente,
    NotaPratica,
    LogAttivitaPratica,
    AnnuncioAI,
)

from .forms import (
    CreaPraticaForm,
    CaricaDocumentoForm,
    NotaPraticaForm,
    CustomUserCreationForm,
    CreaAnnuncioAIForm,
    InfoVenditoreForm, 
    InfoAcquirenteForm
)

def home_view(request):
    return render(request, 'real_estate/home.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profilo = ProfiloUtente.objects.get(user=user)
            profilo.ruolo = form.cleaned_data.get('ruolo')
            profilo.filiale = form.cleaned_data.get('filiale', '')

            if profilo.ruolo == 'titolare_agenzia':
                profilo.logo = form.cleaned_data.get('logo')
                profilo.sito_web = form.cleaned_data.get('sito_web')

            profilo.in_fase_di_registrazione = False
            profilo.save()

            from .utils import invia_email_api_brevo 

            invia_email_api_brevo(
                to_email='legal.fgconsulting@gmail.com',
                subject=f'🆕 Nuova registrazione utente: {user.username}',
                content=f"""
                    <p><strong>Username:</strong> {user.username}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p>L'utente ha completato la registrazione e attende approvazione.</p>
                """
            )

            if user.email:
                invia_email_api_brevo(
                    to_email=user.email,
                    subject='Registrazione ricevuta - FG LEGIS',
                    content=f"""
                        <p>Ciao <strong>{user.username}</strong>,</p>
                        <p>la tua registrazione è stata ricevuta e sarà verificata a breve dal nostro team.</p>
                        <p>Ti aggiorneremo con un'email appena sarà attivata.</p>
                        <br><p>Grazie,<br><strong>FG Consulting</strong></p>
                    """
                )

            messages.success(request, "Registrazione completata. Attendi l’attivazione.")
            return redirect('real_estate:home')

        else:
            messages.error(request, "Errore nella registrazione.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def get_pratiche_per_utente(user):
    profilo = get_object_or_404(ProfiloUtente, user=user)

    if profilo.ruolo == 'admin':
        return PraticaImmobiliare.objects.all()
    elif profilo.ruolo == 'titolare_agenzia':
        store_manager_users = ProfiloUtente.objects.filter(titolare=user, ruolo='store_manager').values_list('user', flat=True)
        agenti_users = ProfiloUtente.objects.filter(titolare__in=store_manager_users, ruolo='agente').values_list('user', flat=True)
        utenti_ids = list(store_manager_users) + list(agenti_users)
        return PraticaImmobiliare.objects.filter(utente__in=utenti_ids)
    elif profilo.ruolo == 'store_manager':
        agenti_users = ProfiloUtente.objects.filter(titolare=user, ruolo='agente').values_list('user', flat=True)
        utenti_ids = list(agenti_users) + [user.id]
        return PraticaImmobiliare.objects.filter(utente__in=utenti_ids)
    elif profilo.ruolo == 'agente':
        return PraticaImmobiliare.objects.filter(utente=user)
    elif profilo.ruolo == 'notaio':
        return PraticaImmobiliare.objects.filter(notaio=user)
    elif profilo.ruolo == 'geometra':
        return PraticaImmobiliare.objects.filter(geometra=user)
    return PraticaImmobiliare.objects.none()


@login_required
def area_personale_view(request):
    profilo = get_object_or_404(ProfiloUtente, user=request.user)
    pratiche = get_pratiche_per_utente(request.user)
    pratiche_info = []

    logo_personalizzato = None
    sito_web_personalizzato = None
    colore_primario = "#001f3f"
    colore_accento = "#ffcc00"

    def estrai_colori_da_sito(sito_url):
        try:
            response = requests.get(sito_url, timeout=4)
            soup = BeautifulSoup(response.text, 'html.parser')
            theme_color = soup.find("meta", attrs={"name": "theme-color"})
            if theme_color and theme_color.get("content"):
                return theme_color["content"], "#ffcc00"
        except Exception:
            pass
        return colore_primario, colore_accento

    if profilo.ruolo == 'titolare_agenzia':
        logo_personalizzato = profilo.logo
        sito_web_personalizzato = profilo.sito_web
        if sito_web_personalizzato:
            colore_primario, colore_accento = estrai_colori_da_sito(sito_web_personalizzato)

    elif profilo.ruolo in ['store_manager', 'agente']:
        if profilo.titolare_id:
            titolare = ProfiloUtente.objects.filter(user=profilo.titolare_id, ruolo='titolare_agenzia').first()
            if titolare:
                logo_personalizzato = titolare.logo
                sito_web_personalizzato = titolare.sito_web
                if sito_web_personalizzato:
                    colore_primario, colore_accento = estrai_colori_da_sito(sito_web_personalizzato)

    for p in pratiche:
        totale = p.documenti.count()
        caricati = p.documenti.filter(file__isnull=False).count()
        pratiche_info.append({
            'pratica': p,
            'totale': totale,
            'caricati': caricati,
        })

    return render(request, 'real_estate/area_personale.html', {
        'pratiche_info': pratiche_info,
        'profilo': profilo,
        'ruoli_per_creare_pratica': ['admin', 'titolare_agenzia', 'store_manager', 'agente'],
        'today': timezone.now().date(),
        'logo_personalizzato': logo_personalizzato,
        'sito_web_personalizzato': sito_web_personalizzato,
        'colore_primario': colore_primario,
        'colore_accento': colore_accento,
    })

@login_required
def crea_pratica_view(request):
        if request.method == 'POST':
            form = CreaPraticaForm(request.POST, user=request.user)
            if form.is_valid():
                pratica = form.save(commit=False)
                pratica.utente = request.user
                if pratica.tipo_pratica != 'altro':
                    pratica.tipo_personalizzato = None
                pratica.save()

                # Invia email automatica se sono assegnati notaio o geometra
                from .utils import invia_email_api_brevo

                if pratica.notaio:
                    invia_email_api_brevo(
                        to_email=pratica.notaio.email,
                        subject='📬 Sei stato assegnato a una nuova pratica - FG LEGIS',
                        content=f"""
                            <p>Ciao {pratica.notaio.username},</p>
                            <p>Sei stato assegnato come <strong>notaio</strong> alla pratica <strong>{pratica.nome_azienda}</strong>.</p>
                            <p>Accedi alla tua area riservata per visualizzare o caricare i documenti necessari.</p>
                            <br>
                            <p>Grazie,<br><strong>FG LEGIS</strong></p>
                        """
                    )
                    # Copia a FG Consulting
                    invia_email_api_brevo(
                        to_email='legal.fgconsulting@gmail.com',
                        subject='🔔 Notaio assegnato a nuova pratica',
                        content=f"Notaio {pratica.notaio.username} assegnato alla pratica {pratica.nome_azienda}."
                    )

                if pratica.geometra:
                    invia_email_api_brevo(
                        to_email=pratica.geometra.email,
                        subject='📬 Sei stato assegnato a una nuova pratica - FG LEGIS',
                        content=f"""
                            <p>Ciao {pratica.geometra.username},</p>
                            <p>Sei stato assegnato come <strong>geometra</strong> alla pratica <strong>{pratica.nome_azienda}</strong>.</p>
                            <p>Accedi alla tua area riservata per visualizzare o caricare i documenti tecnici.</p>
                            <br>
                            <p>Grazie,<br><strong>FG LEGIS</strong></p>
                        """
                    )
                    # Copia a FG Consulting
                    invia_email_api_brevo(
                        to_email='legal.fgconsulting@gmail.com',
                        subject='🔔 Geometra assegnato a nuova pratica',
                        content=f"Geometra {pratica.geometra.username} assegnato alla pratica {pratica.nome_azienda}."
                    )


                documenti_predefiniti = {
                    'preliminare': ['Documento Identità', 'Codice Fiscale', 'Preliminare firmato'],
                    'rogito': ['Planimetria catastale', 'Certificato di destinazione urbanistica', 'Atto di provenienza'],
                    'visura': ['Richiesta visura', 'Visura aggiornata'],
                    'catastale': ['Estratto mappa', 'Scheda catastale', 'Richiesta ufficiale'],
                }

                for nome_doc in documenti_predefiniti.get(pratica.tipo_pratica, []):
                    Documento.objects.create(pratica=pratica, nome=nome_doc)

                LogAttivitaPratica.objects.create(
                    pratica=pratica,
                    utente=request.user,
                    azione="Ha creato una nuova pratica."
                )
                messages.success(request, 'Pratica creata con successo.')
                return redirect('real_estate:area_personale')
        else:
            form = CreaPraticaForm(user=request.user)

        return render(request, 'real_estate/crea_pratica.html', {'form': form})



@login_required
def dettaglio_pratica_view(request, pratica_id):
    pratica = get_object_or_404(PraticaImmobiliare, id=pratica_id)
    profilo = getattr(request.user, 'profiloutente', None)

    if profilo.ruolo != 'admin' and pratica.utente != request.user and pratica.notaio != request.user and pratica.geometra != request.user:
        return redirect('real_estate:area_personale')

    venditore_form = InfoVenditoreForm(request.POST or None, instance=pratica)
    acquirente_form = InfoAcquirenteForm(request.POST or None, instance=pratica)
    documento_form = CaricaDocumentoForm(request.POST or None, request.FILES or None)
    nota_form = NotaPraticaForm()

    documenti_predefiniti = [
        "Antiriciclaggio",
        "Proposta di acquisto",
        "Preliminare",
        "Incarico di mediazione",
        "Incarico FG Consulting",
        "Delega accesso atti",
        "Delega scarico planimetrie"
    ]

    for doc_nome in documenti_predefiniti:
        Documento.objects.get_or_create(pratica=pratica, nome=doc_nome)

    if request.method == 'POST':
        if 'salva_venditore' in request.POST and venditore_form.is_valid():
            venditore_form.save()
            messages.success(request, "Dati venditore aggiornati ✅")
            return redirect('real_estate:dettaglio_pratica', pratica_id=pratica.id)

        if 'salva_acquirente' in request.POST and acquirente_form.is_valid():
            acquirente_form.save()
            messages.success(request, "Dati acquirente aggiornati ✅")
            return redirect('real_estate:dettaglio_pratica', pratica_id=pratica.id)

        if 'upload_documento' in request.POST and documento_form.is_valid():
            for file in request.FILES.getlist('file'):
                nome = file.name
                doc, _ = Documento.objects.get_or_create(pratica=pratica, nome=nome)
                doc.file = file
                doc.caricato_il = timezone.now()
                doc.save()

                from .utils import invia_email_api_brevo
                destinatari = set()

                # Se carica notaio/geometra → avvisare titolare/store/agente
                if profilo.ruolo in ['notaio', 'geometra']:
                    agente = pratica.utente
                    if agente and agente.email:
                        destinatari.add(agente.email)
                    store_manager = getattr(agente.profiloutente, 'titolare', None)
                    if store_manager and store_manager.email:
                        destinatari.add(store_manager.email)
                        titolare = getattr(store_manager.profiloutente, 'titolare', None)
                        if titolare and titolare.email:
                            destinatari.add(titolare.email)

                # Se carica agente/store/titolare → avvisare notaio/geometra
                elif profilo.ruolo in ['agente', 'store_manager', 'titolare_agenzia']:
                    if pratica.notaio and pratica.notaio.email:
                        destinatari.add(pratica.notaio.email)
                    if pratica.geometra and pratica.geometra.email:
                        destinatari.add(pratica.geometra.email)

                for email in destinatari:
                    invia_email_api_brevo(
                        to_email=email,
                        subject='📎 Nuovo documento in pratica',
                        content=f"""
                            <p>È stato caricato un documento <strong>{nome}</strong> nella pratica <strong>{pratica.nome_azienda}</strong>.</p>
                            <p>Utente: {request.user.username} – Ruolo: {profilo.ruolo}</p>
                            <p>Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
                        """
                    )

                invia_email_api_brevo(
                    to_email='legal.fgconsulting@gmail.com',
                    subject='📎 Documento caricato in pratica',
                    content=f"""
                        <p>L'utente <strong>{request.user.username}</strong> ha caricato il documento <strong>{nome}</strong> nella pratica <strong>{pratica.nome_azienda}</strong>.</p>
                        <p>Data: {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
                    """
                )

            messages.success(request, "Documento caricato ✅")
            return redirect('real_estate:dettaglio_pratica', pratica_id=pratica.id)

        if 'aggiungi_nota' in request.POST:
            nota_form = NotaPraticaForm(request.POST)
            if nota_form.is_valid():
                nota = nota_form.save(commit=False)
                nota.pratica = pratica
                nota.autore = request.user
                nota.data_creazione = timezone.now()
                nota.save()
                messages.success(request, 'Nota salvata.')
                return redirect('real_estate:dettaglio_pratica', pratica_id=pratica.id)

        if 'rispondi_nota' in request.POST:
            risposta_a = request.POST.get('risposta_a')
            testo = request.POST.get('testo')
            if risposta_a and testo:
                NotaPratica.objects.create(
                    pratica=pratica,
                    autore=request.user,
                    testo=testo,
                    risposta_a_id=risposta_a,
                    data_creazione=timezone.now()
                )
                messages.success(request, 'Risposta salvata.')
                return redirect('real_estate:dettaglio_pratica', pratica_id=pratica.id)

    note = pratica.note_pratica.select_related('autore').all()
    log = pratica.log_attivita.select_related('utente').all()
    documenti = pratica.documenti.all()
    caricati = [d.nome for d in documenti if d.file]
    mancanti = [d for d in documenti_predefiniti if d not in caricati]
    totale = len(documenti)
    completamento = int((len(caricati) / totale) * 100) if totale > 0 else 0

    return render(request, 'real_estate/dettaglio_pratica.html', {
        'pratica': pratica,
        'documenti': documenti,
        'caricati': caricati,
        'mancanti': mancanti,
        'venditore_form': venditore_form,
        'acquirente_form': acquirente_form,
        'documento_form': documento_form,
        'nota_form': nota_form,
        'note': note,
        'log_attivita': log,
        'profilo': profilo,
        'completamento': completamento,
    })


@login_required
def area_notaio_view(request):
    profilo = get_object_or_404(ProfiloUtente, user=request.user)
    if profilo.ruolo != 'notaio':
        return redirect('real_estate:area_personale')

    if request.method == 'POST':
        pratica_id = request.POST.get('pratica_id')
        nome_documento = request.POST.get('nome_documento')
        if pratica_id and nome_documento:
            pratica = get_object_or_404(PraticaImmobiliare, id=pratica_id, notaio=request.user)
            Documento.objects.create(pratica=pratica, nome=nome_documento)

            from .utils import invia_email_api_brevo

            # Recupera tutti gli utenti collegati alla pratica
            autore = pratica.utente
            store_manager = ProfiloUtente.objects.filter(
                user__in=[autore],
                ruolo='agente'
            ).first().titolare if autore else None

            titolare = None
            if store_manager:
                titolare = ProfiloUtente.objects.filter(user=store_manager, ruolo='store_manager').first().titolare

            destinatari = set()

            if autore and autore.email:
                destinatari.add(autore.email)
            if store_manager and store_manager.email:
                destinatari.add(store_manager.email)
            if titolare and titolare.email:
                destinatari.add(titolare.email)

            # Invia la mail a tutti
            for email in destinatari:
                invia_email_api_brevo(
                    to_email=email,
                    subject='📄 Documento caricato dal notaio/geometra',
                    content=f"""
                        <p>È stato caricato un documento nella pratica <strong>{pratica.nome_azienda}</strong>.</p>
                        <p><strong>Ruolo:</strong> {profilo.ruolo}</p>
                        <p><strong>Utente:</strong> {request.user.username}</p>
                        <p>Accedi alla piattaforma per visualizzarlo.</p>
                    """
                )

            # Copia anche a FG Consulting
            invia_email_api_brevo(
                to_email='legal.fgconsulting@gmail.com',
                subject='📄 Documento caricato da notaio/geometra',
                content=f"{profilo.ruolo} {request.user.username} ha caricato un documento nella pratica {pratica.nome_azienda}."
            )

            LogAttivitaPratica.objects.create(pratica=pratica, utente=request.user, azione=f"Notaio ha richiesto un nuovo documento: “{nome_documento}”.")
            messages.success(request, "Documento richiesto aggiunto con successo.")
            return redirect('real_estate:area_notaio')

    pratiche = PraticaImmobiliare.objects.filter(notaio=request.user)
    return render(request, 'real_estate/area_notaio.html', {'pratiche': pratiche})


@login_required
def area_geometra_view(request):
        profilo = get_object_or_404(ProfiloUtente, user=request.user)
        if profilo.ruolo != 'geometra':
            return redirect('real_estate:area_personale')

        if request.method == 'POST':
            pratica_id = request.POST.get('pratica_id')
            nome_documento = request.POST.get('nome_documento')
            file = request.FILES.get('file')
            if pratica_id and nome_documento and file:
                pratica = get_object_or_404(PraticaImmobiliare, id=pratica_id, geometra=request.user)
                Documento.objects.create(
                    pratica=pratica,
                    nome=nome_documento,
                    file=file,
                    caricato_il=timezone.now()
                )

                from .utils import invia_email_api_brevo

                # Recupera utenti collegati alla pratica
                autore = pratica.utente
                store_manager = ProfiloUtente.objects.filter(
                    user__in=[autore],
                    ruolo='agente'
                ).first().titolare if autore else None

                titolare = None
                if store_manager:
                    titolare = ProfiloUtente.objects.filter(user=store_manager, ruolo='store_manager').first().titolare

                destinatari = set()

                if autore and autore.email:
                    destinatari.add(autore.email)
                if store_manager and store_manager.email:
                    destinatari.add(store_manager.email)
                if titolare and titolare.email:
                    destinatari.add(titolare.email)

                # Invia email a ogni destinatario
                for email in destinatari:
                    invia_email_api_brevo(
                        to_email=email,
                        subject='📄 Documento caricato dal geometra',
                        content=f"""
                            <p>È stato caricato un documento tecnico nella pratica <strong>{pratica.nome_azienda}</strong>.</p>
                            <p><strong>Geometra:</strong> {request.user.username}</p>
                            <p>Accedi alla piattaforma per visualizzarlo.</p>
                        """
                    )

                # Copia anche a FG Consulting
                invia_email_api_brevo(
                    to_email='legal.fgconsulting@gmail.com',
                    subject='📄 Documento caricato dal geometra',
                    content=f"Geometra {request.user.username} ha caricato un documento nella pratica {pratica.nome_azienda}."
                )

                LogAttivitaPratica.objects.create(
                    pratica=pratica,
                    utente=request.user,
                    azione=f"Geometra ha caricato un documento tecnico: '{nome_documento}'."
                )
                messages.success(request, "Documento tecnico caricato con successo.")
                return redirect('real_estate:area_geometra')

        pratiche = PraticaImmobiliare.objects.filter(geometra=request.user)
        return render(request, 'real_estate/area_geometra.html', {'pratiche': pratiche})

@login_required
def crea_annuncio_ai_view(request, pratica_id):
    pratica = get_object_or_404(PraticaImmobiliare, id=pratica_id)
    profilo = get_object_or_404(ProfiloUtente, user=request.user)
    if profilo.ruolo not in ['admin', 'titolare_agenzia', 'store_manager', 'agente']:
        return redirect('real_estate:area_personale')
    if profilo.ruolo == 'agente' and pratica.utente != request.user:
        return redirect('real_estate:area_personale')

    if request.method == 'POST':
        form = CreaAnnuncioAIForm(request.POST, request.FILES)
        if form.is_valid():
            annuncio = form.save(commit=False)
            annuncio.utente = request.user
            annuncio.pratica = pratica
            annuncio.save()
            messages.success(request, "Annuncio AI creato. L'elaborazione inizierà a breve.")
            return redirect('real_estate:area_personale')
    else:
        form = CreaAnnuncioAIForm()

    return render(request, 'real_estate/crea_annuncio_ai.html', {'form': form, 'pratica': pratica})
