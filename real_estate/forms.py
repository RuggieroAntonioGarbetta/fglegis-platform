from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PraticaImmobiliare, NotaPratica, AnnuncioAI, ProfiloUtente


# ✅ Form personalizzato per la registrazione con scelta ruolo e branding
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Inserisci una email valida.",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    ruolo = forms.ChoiceField(
        choices=[('', 'Seleziona ruolo')] + ProfiloUtente._meta.get_field('ruolo').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    filiale = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filiale'})
    )

    logo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    sito_web = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.miosito.it'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "ruolo", "filiale", "logo", "sito_web")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Conferma Password'
        })

        # ✅ Nasconde logo e sito SOLO dopo il submit se non è titolare
        if self.data and self.data.get('ruolo') != 'titolare_agenzia':
            self.fields['logo'].widget = forms.HiddenInput()
            self.fields['sito_web'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profilo = ProfiloUtente.objects.get(user=user)
            profilo.ruolo = self.cleaned_data["ruolo"]
            profilo.filiale = self.cleaned_data.get("filiale", "")

            if profilo.ruolo == "titolare_agenzia":
                profilo.logo = self.cleaned_data.get("logo")
                profilo.sito_web = self.cleaned_data.get("sito_web")

            profilo.in_fase_di_registrazione = False
            profilo.save()
        return user


    # ✅ Form per creazione pratica immobiliare
class CreaPraticaForm(forms.ModelForm):
        class Meta:
            model = PraticaImmobiliare
            fields = ['nome_azienda', 'tipo_pratica', 'tipo_personalizzato', 'notaio', 'geometra']
            widgets = {
                'nome_azienda': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Nome azienda'
                }),
                'tipo_pratica': forms.Select(attrs={'class': 'form-control'}),
                'tipo_personalizzato': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Specificare tipo se "Altro"'
                }),
                'notaio': forms.Select(attrs={'class': 'form-control'}),
                'geometra': forms.Select(attrs={'class': 'form-control'}),
            }

        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None)
            super().__init__(*args, **kwargs)

            if user:
                profilo = getattr(user, 'profiloutente', None)
                if not profilo or profilo.ruolo != 'admin':
                    self.fields.pop('notaio', None)
                    self.fields.pop('geometra', None)


# ✅ Form per caricamento singolo documento
class CaricaDocumentoForm(forms.Form):
    file = forms.FileField(
        label='Carica documento',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )


# ✅ Form per inserimento note nella pratica
class NotaPraticaForm(forms.ModelForm):
    class Meta:
        model = NotaPratica
        fields = ['testo']
        widgets = {
            'testo': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Scrivi una nota...',
                'class': 'form-control'
            }),
        }


# ✅ Form per creazione annuncio AI
class CreaAnnuncioAIForm(forms.ModelForm):
    class Meta:
        model = AnnuncioAI
        fields = ['titolo', 'descrizione', 'tipologia', 'immagini', 'video']
        widgets = {
            'titolo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titolo annuncio'
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrizione dettagliata dell\'immobile (obbligatoria)',
                'rows': 5
            }),
            'tipologia': forms.Select(attrs={'class': 'form-control'}),
            'immagini': forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipologia = cleaned_data.get("tipologia")
        immagini = self.files.getlist("immagini")
        video = cleaned_data.get("video")

        if tipologia == 'foto' and not immagini:
            raise forms.ValidationError("Hai selezionato 'Carica Foto' ma non hai caricato alcuna immagine.")
        if tipologia == 'video' and not video:
            raise forms.ValidationError("Hai selezionato 'Carica Video' ma non hai caricato alcun file video.")

        return cleaned_data

# ✅ Form per i dati venditore
class InfoVenditoreForm(forms.ModelForm):
    class Meta:
        model = PraticaImmobiliare
        fields = ['venditore_nome', 'venditore_cognome', 'venditore_indirizzo', 'venditore_email', 'venditore_cellulare']
        widgets = {
            'venditore_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'venditore_cognome': forms.TextInput(attrs={'class': 'form-control'}),
            'venditore_indirizzo': forms.TextInput(attrs={'class': 'form-control'}),
            'venditore_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'venditore_cellulare': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ✅ Form per i dati acquirente
class InfoAcquirenteForm(forms.ModelForm):
    class Meta:
        model = PraticaImmobiliare
        fields = ['acquirente_nome', 'acquirente_cognome', 'acquirente_email', 'acquirente_cellulare']
        widgets = {
            'acquirente_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'acquirente_cognome': forms.TextInput(attrs={'class': 'form-control'}),
            'acquirente_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'acquirente_cellulare': forms.TextInput(attrs={'class': 'form-control'}),
        }
