from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from ..models import Kisi, Album, Sarki
from ..forms import AlbumForm, SarkiForm
import logging

logger = logging.getLogger(__name__)

def sarki_sozleri(request):
    harf = request.GET.get('harf', '').lower()
    harfler = ['a', 'b', 'c', 'ç', 'd', 'e', 'ê', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ş', 't', 'u', 'û', 'v', 'w', 'x', 'y', 'z']
    
    kisi_gruplari = []
    if harf:
        # Sadece seçili harfle başlayan ve şarkı sözü eklenmiş kişileri al
        kisiler = Kisi.objects.filter(
            Q(ad__istartswith=harf) & Q(albumler__sarkilar__isnull=False)
        ).distinct().order_by('ad').annotate(
            album_sayisi=Count('albumler', distinct=True),
            sarki_sayisi=Count('albumler__sarkilar', distinct=True)
        )
        if kisiler.exists():
            kisi_gruplari.append((harf, kisiler))
    else:
        # Tüm harfler için, sadece şarkı sözü eklenmiş kişileri al
        for h in harfler:
            kisiler = Kisi.objects.filter(
                Q(ad__istartswith=h) & Q(albumler__sarkilar__isnull=False)
            ).distinct().order_by('ad').annotate(
                album_sayisi=Count('albumler', distinct=True),
                sarki_sayisi=Count('albumler__sarkilar', distinct=True)
            )
            if kisiler.exists():
                kisi_gruplari.append((h, kisiler))
    
    return render(request, 'main/sarki/sarki_sozleri.html', {
        'harfler': harfler,
        'kisi_gruplari': kisi_gruplari,
        'secili_harf': harf
    })

@login_required
@csrf_protect
def sarki_kisi_ara(request):
    query = request.GET.get('q', '').strip().lower()
    kisiler = Kisi.objects.filter(ad__istartswith=query).order_by('ad')[:20]
    data = [{
        'id': kisi.id,
        'ad': kisi.ad,
        'biyografi': kisi.biyografi[:100] + ('...' if len(kisi.biyografi) > 100 else '')
    } for kisi in kisiler]
    return JsonResponse({'kisiler': data})

@login_required
@csrf_protect
def sarki_ekle(request):
    kisi_id = request.GET.get('kisi_id')
    kisi = None
    albumler = []
    if kisi_id:
        kisi = get_object_or_404(Kisi, id=kisi_id)
        albumler = Album.objects.filter(kisi=kisi).order_by('ad')
    
    album_form = AlbumForm()
    sarki_form = SarkiForm()
    
    if request.method == 'POST':
        if 'album_submit' in request.POST:
            album_form = AlbumForm(request.POST)
            if album_form.is_valid() and kisi:
                album = album_form.save(commit=False)
                album.kisi = kisi
                album.kullanici = request.user
                album.save()
                logger.info(f"Albüm eklendi: {album.ad}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': album_form.errors.as_json()})
        elif 'sarki_submit' in request.POST:
            sarki_form = SarkiForm(request.POST)
            album_id = request.POST.get('album_id')
            if sarki_form.is_valid() and album_id:
                album = get_object_or_404(Album, id=album_id)
                sarki = sarki_form.save(commit=False)
                sarki.album = album
                sarki.kullanici = request.user
                sarki.save()
                logger.info(f"Şarkı eklendi: {sarki.ad}, Kullanıcı: {request.user.username}")
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': sarki_form.errors.as_json()})
    
    return render(request, 'main/sarki/sarki_ekle.html', {
        'kisi': kisi,
        'albumler': albumler,
        'album_form': album_form,
        'sarki_form': sarki_form
    })

@login_required
@csrf_protect
def sarki_album_liste(request, kisi_id):
    kisi = get_object_or_404(Kisi, id=kisi_id)
    albumler = Album.objects.filter(kisi=kisi).order_by('ad')
    return render(request, 'main/sarki/album_liste.html', {
        'kisi': kisi,
        'albumler': albumler
    })

@login_required
@csrf_protect
def sarki_liste(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    sarkilar = Sarki.objects.filter(album=album).order_by('ad')
    return render(request, 'main/sarki/sarki_liste.html', {
        'album': album,
        'sarkilar': sarkilar
    })

@login_required
@csrf_protect
def sarki_detay(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    return render(request, 'main/sarki/sarki_detay.html', {'sarki': sarki})

@login_required
@csrf_protect
@require_POST
def sarki_sil(request, sarki_id):
    sarki = get_object_or_404(Sarki, id=sarki_id)
    if sarki.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu şarkıyı silme yetkiniz yok.'}, status=403)
    sarki.delete()
    logger.info(f"Şarkı silindi: {sarki.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})

@login_required
@csrf_protect
@require_POST
def sarki_album_sil(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    if album.kullanici != request.user:
        return JsonResponse({'success': False, 'error': 'Bu albümü silme yetkiniz yok.'}, status=403)
    album.delete()
    logger.info(f"Albüm silindi: {album.ad}, Kullanıcı: {request.user.username}")
    return JsonResponse({'success': True})