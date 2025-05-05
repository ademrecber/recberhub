from django import forms
from .models import Post, Comment, Critique, CritiqueVote, Sozluk, Kisi, Album, Sarki, Atasozu, Deyim
import bleach
import re

def clean_form_text(text, allowed_tags=['p', 'b', 'i']):
    """Ortak metin temizleme fonksiyonu."""
    if not text.strip():
        raise forms.ValidationError("Bu alan boş olamaz.")
    return bleach.clean(text, tags=allowed_tags, strip=False)

class PostForm(forms.ModelForm):
    link = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'text', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Eleştiri Başlığı'}),
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Bir eleştiri paylaş...'}),
            'link': forms.URLInput(attrs={'class': 'form-control border-0 mt-2', 'placeholder': 'Link ekle (isteğe bağlı)'})
        }

    def clean_text(self):
        return clean_form_text(self.cleaned_data['text'], allowed_tags=['p', 'br', 'img'])

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Yorum yap...', 'maxlength': 500})
        }

    def clean_text(self):
        text = clean_form_text(self.cleaned_data['text'])
        if len(text) > 500:
            raise forms.ValidationError("Yorum 500 karakterden uzun olamaz.")
        return text

class CritiqueForm(forms.ModelForm):
    class Meta:
        model = Critique
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control border-0 auto-grow', 'placeholder': 'Eleştirinizi yazın...', 'maxlength': 5000})
        }

    def clean_text(self):
        text = clean_form_text(self.cleaned_data['text'], allowed_tags=['p', 'b', 'i', 'img'])
        if len(text) > 5000:
            raise forms.ValidationError("Değerlendirme 5000 karakterden uzun olamaz.")
        return text

class CritiqueVoteForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = CritiqueVote
        fields = ['rating']

class SozlukForm(forms.ModelForm):
    class Meta:
        model = Sozluk
        fields = ['kelime', 'detay']
        widgets = {
            'kelime': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kelime girin', 'required': True}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Kelime detayını girin', 'rows': 4, 'required': True}),
        }

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError('Kelime alanı zorunludur.')
        if Sozluk.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Bu kelime zaten sözlükte mevcut, lütfen farklı bir kelime girin.')
        return kelime

class KisiForm(forms.ModelForm):
    class Meta:
        model = Kisi
        fields = ['ad', 'biyografi', 'kategoriler']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kişinin adını girin', 'required': True}),
            'biyografi': forms.Textarea(attrs={'class': 'form-control d-none', 'id': 'biyografi-hidden', 'required': True}),
            'kategoriler': forms.SelectMultiple(attrs={'class': 'form-control select2', 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Ad alanı zorunludur.')
        return ad

    def clean_biyografi(self):
        biyografi = self.cleaned_data.get('biyografi')
        if not biyografi.strip():
            raise forms.ValidationError('Biyografi alanı zorunludur.')
        return biyografi

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['ad']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Albüm adını girin', 'required': True}),
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Albüm adı zorunludur.')
        return ad

class SarkiForm(forms.ModelForm):
    link = forms.URLField(required=False)

    class Meta:
        model = Sarki
        fields = ['ad', 'sozler', 'link']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şarkı adını girin', 'required': True}),
            'sozler': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Şarkı sözlerini girin', 'rows': 6, 'required': True}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Şarkı linki (isteğe bağlı)'})
        }

    def clean_ad(self):
        ad = self.cleaned_data.get('ad')
        if not ad.strip():
            raise forms.ValidationError('Şarkı adı zorunludur.')
        return ad

    def clean_sozler(self):
        sozler = self.cleaned_data.get('sozler')
        if not sozler.strip():
            raise forms.ValidationError('Şarkı sözleri zorunludur.')
        return sozler

class AtasozuDeyimForm(forms.Form):
    tur = forms.ChoiceField(
        choices=[('atasozu', 'Atasözü'), ('deyim', 'Deyim')],
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        label='Tür'
    )
    kelime = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kelime girin', 'required': True}),
        label='Kelime'
    )
    anlami = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Anlamını girin', 'rows': 4, 'required': True}),
        label='Anlam'
    )
    ornek = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Örnek kullanım (isteğe bağlı)', 'rows': 4}),
        label='Örnek'
    )

    def clean_kelime(self):
        kelime = self.cleaned_data.get('kelime')
        if not kelime.strip():
            raise forms.ValidationError('Kelime alanı zorunludur.')
        if not re.match(r'^[a-zçêîşû\s]+$', kelime.lower()):
            raise forms.ValidationError('Kelime sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).')
        tur = self.cleaned_data.get('tur')
        if tur == 'atasozu' and Atasozu.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Bu atasözü zaten mevcut, lütfen farklı bir kelime girin.')
        if tur == 'deyim' and Deyim.objects.filter(kelime__iexact=kelime).exists():
            raise forms.ValidationError('Bu deyim zaten mevcut, lütfen farklı bir kelime girin.')
        return kelime

    def clean_anlami(self):
        anlami = self.cleaned_data.get('anlami')
        return clean_form_text(anlami)

    def clean_ornek(self):
        ornek = self.cleaned_data.get('ornek', '')
        if ornek:
            return clean_form_text(ornek)
        return ornek