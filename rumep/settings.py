from pathlib import Path
import dj_database_url
import os

     # Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

     # Quick-start development settings - unsuitable for production
     # See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

     # SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$km6au=v0s&=1vyo+hjox6awd%-12a6n8pzapa@7w)za^rgj1^'  # Render'da ortam değişkeniyle değiştirilecek

     # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']  # Test için, sonra ['rumep-test.onrender.com'] yap

     # Application definition

INSTALLED_APPS = [
         'django.contrib.admin',
         'django.contrib.auth',
         'django.contrib.contenttypes',
         'django.contrib.sessions',
         'django.contrib.messages',
         'django.contrib.staticfiles',
         'django.contrib.humanize',  # humanize kütüphanesi eklendi
         'social_django',
         'main',
         ]

MIDDLEWARE = [
         'django.middleware.security.SecurityMiddleware',
         'django.contrib.sessions.middleware.SessionMiddleware',
         'django.middleware.common.CommonMiddleware',
         'django.middleware.csrf.CsrfViewMiddleware',
         'django.contrib.auth.middleware.AuthenticationMiddleware',
         'django.contrib.messages.middleware.MessageMiddleware',
         'django.middleware.clickjacking.XFrameOptionsMiddleware',
         'main.middleware.SocialAuthExceptionMiddleware',
     ]

ROOT_URLCONF = 'rumep.urls'

TEMPLATES = [
         {
             'BACKEND': 'django.template.backends.django.DjangoTemplates',
             'DIRS': [],
             'APP_DIRS': True,
             'OPTIONS': {
                 'context_processors': [
                     'django.template.context_processors.debug',
                     'django.template.context_processors.request',
                     'django.contrib.auth.context_processors.auth',
                     'django.contrib.messages.context_processors.messages',
                 ],
             },
         },
     ]

WSGI_APPLICATION = 'rumep.wsgi.application'

     # Database
     # https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
         'default': dj_database_url.config(default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
     }

     # Password validation
     # https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
         {
             'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
         },
         {
             'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
         },
         {
             'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
         },
         {
             'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
         },
     ]

     # Internationalization
     # https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

     # Static files (CSS, JavaScript, Images)
     # https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "main/static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

     # Default primary key field type
     # https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
         'social_core.backends.google.GoogleOAuth2',  # Google ile giriş
         'social_core.backends.twitter.TwitterOAuth',  # Twitter ile giriş (sonra ekleriz)
         'django.contrib.auth.backends.ModelBackend',  # Varsayılan Django giriş
     )

     # Google için (şimdilik Twitter'ı atlayabiliriz)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', 'default-key')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', 'default-secret')

LOGIN_URL = '/login/'  # Giriş yapmamışsa buraya gider
LOGIN_REDIRECT_URL = '/'  # Giriş sonrası ana sayfa
LOGOUT_REDIRECT_URL = '/login/'  # Çıkış sonrası giriş sayfası

SOCIAL_AUTH_LOGIN_ERROR_URL = '/login/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_PIPELINE = (
         'social_core.pipeline.social_auth.social_details',
         'social_core.pipeline.social_auth.social_uid',
         'social_core.pipeline.social_auth.auth_allowed',
         'social_core.pipeline.social_auth.social_user',
         'social_core.pipeline.user.get_username',
         'social_core.pipeline.user.create_user',
         'social_core.pipeline.social_auth.associate_user',
         'social_core.pipeline.social_auth.load_extra_data',
         'social_core.pipeline.user.user_details',
     )

     # Katkı puanları
KATKI_PUANLARI = {
         'sarki': 5,
         'kisi': 3,
         'sozluk': 2,
         'atasozu': 2,
         'deyim': 2,
     }
