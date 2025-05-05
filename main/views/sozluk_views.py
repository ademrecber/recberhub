from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from ..models import Sozluk
from ..forms import SozlukForm
import bleach
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
def sozluk_ana_sayfa(request):
    if request.method == 'POST':
        form = SozlukForm(request.POST)
        if form.is_valid():
            sozluk = form.save(commit=False)
            sozluk.kullanici = request.user
            sozluk.kelime = bleach.clean(sozluk.kelime, tags=[], strip=True).lower()
            sozluk.detay = bleach.clean(sozluk.detay, tags=['p', 'br'], strip=True)
            try:
                sozluk.save()
                logger.info(f"Kelime eklendi: {sozluk.kelime}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'errors': {field: errors[0] for field, errors in e.message_dict.items()}})
        return JsonResponse({'success': False, 'errors': {field: errors[0]['message'] for field, errors in form.errors.get_json_data().items()}})
    
    form = SozlukForm()
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    # Tüm kelimeleri alfabetik sırayla gruplandır
    kelime_gruplari = []
    for harf in harfler:
        kelimeler = Sozluk.objects.filter(kelime__istartswith=harf).order_by('kelime')
        if kelimeler.exists():
            kelime_gruplari.append((harf, kelimeler))
    
    return render(request, 'main/sozluk/sozluk.html', {
        'form': form,
        'harfler': harfler,
        'kelime_gruplari': kelime_gruplari
    })

def sozluk_harf(request, harf):
    if harf.lower() not in ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']:
        return redirect('sozluk_ana_sayfa')
    kelimeler = Sozluk.objects.filter(kelime__istartswith=harf).order_by('kelime')[:20]
    return render(request, 'main/sozluk/sozluk_harf.html', {'harf': harf, 'kelimeler': kelimeler, 'user': request.user})

@csrf_protect
def sozluk_harf_yukle(request):
    harf = request.GET.get('harf')
    offset = int(request.GET.get('offset', 0))
    limit = 20
    if harf.lower() not in ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']:
        return JsonResponse({'error': 'Geçersiz harf'}, status=400)
    kelimeler = Sozluk.objects.filter(kelime__istartswith=harf).order_by('kelime')[offset:offset + limit]
    data = [{
        'id': kelime.id,
        'kelime': kelime.kelime,
        'detay': kelime.detay[:100] + ('...' if len(kelime.detay) > 100 else ''),
        'is_owner': kelime.kullanici == request.user
    } for kelime in kelimeler]
    has_more = Sozluk.objects.filter(kelime__istartswith=harf).count() > offset + limit
    return JsonResponse({'kelimeler': data, 'has_more': has_more})

def sozluk_kelime(request, kelime_id):
    kelime = get_object_or_404(Sozluk, id=kelime_id)
    return render(request, 'main/sozluk/sozluk_kelime.html', {'kelime': kelime, 'user': request.user})

@login_required
@csrf_protect
def sozluk_kelime_sil(request, kelime_id):
    kelime = get_object_or_404(Sozluk, id=kelime_id)
    if kelime.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu kelimeyi silme yetkiniz yok.'}, status=403)
    kelime.delete()
    logger.info(f"Kelime silindi: {kelime.kelime}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})