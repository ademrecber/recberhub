from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
import re

def generate_short_id():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_id = models.CharField(max_length=8, unique=True, default=generate_short_id, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    text = models.TextField(max_length=10000)
    link = models.CharField(max_length=100, blank=True, null=True, unique=True)  # Kısa link (rmp/<kısa_kod>)
    original_link = models.URLField(blank=True, null=True)  # Uzun URL
    embed_code = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_posts', blank=True)
    views = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.title[:20] if self.title else self.text[:20]}"

    def like_count(self):
        return self.likes.count()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    username = models.CharField(max_length=30, unique=True)
    instagram_username = models.CharField(max_length=30, blank=True, null=True)
    twitter_username = models.CharField(max_length=30, blank=True, null=True)
    posts_visible = models.BooleanField(default=True)
    critiques_visible = models.BooleanField(default=True)
    comments_visible = models.BooleanField(default=True)
    katki_puani = models.PositiveIntegerField(default=0)  # Katkı puanı
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Aktif'),
            ('frozen', 'Dondurulmuş'),
            ('deletion_scheduled', 'Silinme Planlandı')
        ],
        default='active'
    )
    scheduled_deletion_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.nickname

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"

class Critique(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_id = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='critiques')
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = '?' + generate_short_id()
        super().save(*args, **kwargs)

class CritiqueVote(models.Model):
    critique = models.ForeignKey(Critique, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('critique', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.critique.short_id} - {self.rating}"

class PostVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=[('up', 'Upvote'), ('down', 'Downvote')])
    class Meta:
        unique_together = ('user', 'post')

class CommentVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=[('up', 'Upvote'), ('down', 'Downvote')])
    class Meta:
        unique_together = ('user', 'comment')

class Sozluk(models.Model):
    kelime = models.CharField(max_length=50, db_index=True, unique=True)
    detay = models.TextField(max_length=500)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['kelime']
        verbose_name = 'Sözlük'
        verbose_name_plural = 'Sözlük'

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.kelime.lower()):
            raise ValidationError({'kelime': 'Kelime sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'})
        if not self.detay.strip():
            raise ValidationError({'detay': 'Detay alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        # Katkı kaydı oluştur
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='sozluk',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['sozluk']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['sozluk']
        self.kullanici.profile.save()

    def __str__(self):
        return self.kelime

class Kategori(models.Model):
    ad = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.ad

class Kisi(models.Model):
    ad = models.CharField(max_length=100, db_index=True)
    biyografi = models.TextField(max_length=20000)
    kategoriler = models.ManyToManyField(Kategori)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['ad']
        verbose_name = 'Kişi'
        verbose_name_plural = 'Kişiler'

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.ad.lower()):
            raise ValidationError({'ad': 'Ad sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'})
        if not self.biyografi.strip():
            raise ValidationError({'biyografi': 'Biyografi alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Katkı kaydı oluştur
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='kisi',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['kisi']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['kisi']
        self.kullanici.profile.save()

    def __str__(self):
        return self.ad

class Album(models.Model):
    kisi = models.ForeignKey(Kisi, on_delete=models.CASCADE, related_name='albumler')
    ad = models.CharField(max_length=100)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['ad']
        verbose_name = 'Albüm'
        verbose_name_plural = 'Albümler'

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': 'Albüm adı zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kisi.ad} - {self.ad}"

class Sarki(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='sarkilar')
    ad = models.CharField(max_length=100)
    sozler = models.TextField(max_length=10000)
    link = models.URLField(blank=True, null=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['ad']
        verbose_name = 'Şarkı'
        verbose_name_plural = 'Şarkılar'

    def clean(self):
        if not self.ad.strip():
            raise ValidationError({'ad': 'Şarkı adı zorunludur.'})
        if not self.sozler.strip():
            raise ValidationError({'sozler': 'Şarkı sözleri zorunludur.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Katkı kaydı oluştur
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='sarki',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['sarki']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['sarki']
        self.kullanici.profile.save()

    def __str__(self):
        return f"{self.album.ad} - {self.ad}"

class Atasozu(models.Model):
    kelime = models.CharField(max_length=100, db_index=True, unique=True)
    anlami = models.TextField(max_length=500)
    ornek = models.TextField(max_length=500, blank=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['kelime']
        verbose_name = 'Atasözü'
        verbose_name_plural = 'Atasözleri'

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.kelime.lower()):
            raise ValidationError({'kelime': 'Kelime sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'})
        if not self.anlami.strip():
            raise ValidationError({'anlami': 'Anlam alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        # Katkı kaydı oluştur
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='atasozu',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['atasozu']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['atasozu']
        self.kullanici.profile.save()

    def __str__(self):
        return self.kelime

class Deyim(models.Model):
    kelime = models.CharField(max_length=100, db_index=True, unique=True)
    anlami = models.TextField(max_length=500)
    ornek = models.TextField(max_length=500, blank=True)
    kullanici = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['kelime']
        verbose_name = 'Deyim'
        verbose_name_plural = 'Deyimler'

    def clean(self):
        if not re.match(r'^[a-zçêîşû\s]+$', self.kelime.lower()):
            raise ValidationError({'kelime': 'Kelime sadece Kürtçe harfler içerebilir (a-z, ç, ê, î, ş, û ve boşluk).'})
        if not self.anlami.strip():
            raise ValidationError({'anlami': 'Anlam alanı zorunludur.'})

    def save(self, *args, **kwargs):
        self.kelime = self.kelime.upper()
        self.full_clean()
        super().save(*args, **kwargs)
        # Katkı kaydı oluştur
        from django.conf import settings
        Katki.objects.create(
            user=self.kullanici,
            tur='deyim',
            icerik_id=self.id,
            puan=settings.KATKI_PUANLARI['deyim']
        )
        self.kullanici.profile.katki_puani += settings.KATKI_PUANLARI['deyim']
        self.kullanici.profile.save()

    def __str__(self):
        return self.kelime

class Katki(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='katkilar')
    tur = models.CharField(
        max_length=20,
        choices=[
            ('sarki', 'Şarkı Sözü'),
            ('kisi', 'Kişi'),
            ('sozluk', 'Sözlük'),
            ('atasozu', 'Atasözü'),
            ('deyim', 'Deyim')
        ]
    )
    icerik_id = models.PositiveIntegerField()
    puan = models.PositiveIntegerField()
    eklenme_tarihi = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-eklenme_tarihi']
        verbose_name = 'Katkı'
        verbose_name_plural = 'Katkılar'

    def __str__(self):
        return f"{self.user.username} - {self.tur} - {self.eklenme_tarihi}"