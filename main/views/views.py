from .home_views import home
from .post_views import delete_post, post_detail, like_post, load_more, vote_post, vote_comment, add_critique, list_critiques, delete_critique, vote_critique, popular_critiques
from .popular_views import popular, load_more_popular
from .profile_views import login_page, complete_profile, profile, update_profile, search, unlike_post, profile_delete_comment, profile_delete_post, profile_delete_critique
from .comment_views import delete_comment, build_comment_tree
from .sozluk_views import sozluk_ana_sayfa, sozluk_harf, sozluk_harf_yukle, sozluk_kelime, sozluk_kelime_sil
from .kisi_views import kisi_detay, kisi_ekle, kisi_liste, kisi_liste_yukle, kisi_sil
from .sarki_views import sarki_kisi_ara, sarki_album_liste, sarki_liste, sarki_detay, sarki_sil, sarki_sozleri, sarki_ekle, sarki_album_sil
from .atasozu_deyim_views import atasozu_deyim, atasozu_deyim_detay, atasozu_deyim_sil, atasozu_deyim_ekle
from .katki_views import load_more_liderler, load_more_katkilar
from .base import profile_required
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'main/404.html', status=404)