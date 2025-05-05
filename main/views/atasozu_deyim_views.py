from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db.models import Q
from ..models import Atasozu, Deyim
from ..forms import AtasozuDeyimForm
import logging

logger = logging.getLogger(__name__)

def atasozu_deyim(request):
    harf = request.GET.get('harf', '').lower()
    sekme = request.GET.get('sekme', 'atasozu')
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    atasozu_gruplari = []
    deyim_gruplari = []
    
    # Atasözleri için gruplar
    if sekme == 'atasozu' or not sekme:
        if harf:
            # Sadece seçili harfle başlayan atasözlerini al
            atasozleri = Atasozu.objects.filter(kelime__istartswith=harf).order_by('kelime')
            if atasozleri.exists():
                atasozu_gruplari.append((harf, atasozleri))
        else:
            # Tüm harfler için atasözlerini al
            for h in harfler:
                atasozleri = Atasozu.objects.filter(kelime__istartswith=h).order_by('kelime')
                if atasozleri.exists():
                    atasozu_gruplari.append((h, atasozleri))
    
    # Deyimler için gruplar
    if sekme == 'deyim':
        if harf:
            # Sadece seçili harfle başlayan deyimleri al
            deyimler = Deyim.objects.filter(kelime__istartswith=harf).order_by('kelime')
            if deyimler.exists():
                deyim_gruplari.append((harf, deyimler))
        else:
            # Tüm harfler için deyimleri al
            for h in harfler:
                deyimler = Deyim.objects.filter(kelime__istartswith=h).order_by('kelime')
                if deyimler.exists():
                    deyim_gruplari.append((h, deyimler))
    
    return render(request, 'main/atasozu_deyim/atasozu_deyim.html', {
        'harfler': harfler,
        'atasozu_gruplari': atasozu_gruplari,
        'deyim_gruplari': deyim_gruplari,
        'secili_harf': harf,
        'sekme': sekme
    })

@login_required
@csrf_protect
def atasozu_deyim_ekle(request):
    if request.method == 'POST':
        form = AtasozuDeyimForm(request.POST)
        if form.is_valid():
            tur = form.cleaned_data['tur']
            kelime = form.cleaned_data['kelime'].upper()
            anlami = form.cleaned_data['anlami']
            ornek = form.cleaned_data['ornek']
            
            if tur == 'atasozu':
                atasozu = Atasozu(
                    kelime=kelime,
                    anlami=anlami,
                    ornek=ornek,
                    kullanici=request.user
                )
                atasozu.save()
                logger.info(f"Atasözü eklendi: {kelime}, Kullanıcı: {request.user.username}")
            else:
                deyim = Deyim(
                    kelime=kelime,
                    anlami=anlami,
                    ornek=ornek,
                    kullanici=request.user
                )
                deyim.save()
                logger.info(f"Deyim eklendi: {kelime}, Kullanıcı: {request.user.username}")
            
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    
    form = AtasozuDeyimForm()
    return render(request, 'main/atasozu_deyim/atasozu_deyim_ekle.html', {'form': form})

@login_required
@csrf_protect
def atasozu_deyim_detay(request, tur, id):
    if tur == 'atasozu':
        item = get_object_or_404(Atasozu, id=id)
    else:
        item = get_object_or_404(Deyim, id=id)
    return render(request, 'main/atasozu_deyim/atasozu_deyim_detay.html', {
        'item': item,
        'tur': tur
    })

@login_required
@csrf_protect
@require_POST
def atasozu_deyim_sil(request, tur, id):
    if tur == 'atasozu':
        item = get_object_or_404(Atasozu, id=id)
    else:
        item = get_object_or_404(Deyim, id=id)
    
    if item.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu öğeyi silme yetkiniz yok.'}, status=403)
    
    item.delete()
    logger.info(f"{tur.capitalize()} silindi: {item.kelime}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})