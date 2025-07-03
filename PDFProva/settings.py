# settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA E AMBIENTE
# ==============================================================================

# A SECRET_KEY é lida da variável de ambiente. NUNCA a deixe no código!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')

# DEBUG é True localmente, mas False em produção (Render define NODE_ENV).
DEBUG = os.getenv('NODE_ENV') != 'production'

# Configura os hosts permitidos
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Em desenvolvimento local, permita localhost
if DEBUG:
    ALLOWED_HOSTS.append('127.0.0.1')
    ALLOWED_HOSTS.append('localhost')


# ==============================================================================
# APLICAÇÕES E MIDDLEWARE
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'converter',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # CORRIGIDO: Adicionado logo após o SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PDFProva.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'PDFProva.wsgi.application'

# ==============================================================================
# BANCO DE DADOS
# ==============================================================================

DATABASES = {
    'default': dj_database_url.config(
        # Usa a DATABASE_URL do Render em produção
        # Se não encontrar, usa o sqlite local para desenvolvimento
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

# ==============================================================================
# VALIDAÇÃO DE SENHA E INTERNACIONALIZAÇÃO
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'  # Alterado para português do Brasil
TIME_ZONE = 'America/Sao_Paulo' # Alterado para o fuso horário de São Paulo
USE_I18N = True
USE_TZ = True


# ==============================================================================
# ARQUIVOS ESTÁTICOS E DE MÍDIA
# ==============================================================================

# URL para acessar os arquivos estáticos
STATIC_URL = '/static/'
# Diretório onde o `collectstatic` irá juntar todos os arquivos para produção
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Configuração do WhiteNoise para servir arquivos estáticos de forma otimizada
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Diretórios onde o Django procura por arquivos estáticos durante o desenvolvimento
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Configuração para arquivos de mídia (uploads de usuários) - para o futuro
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join('/var/data', 'media') # Lembre-se, isso é para desenvolvimento local

ALLOWED_HOSTS = ['convertpdf.com.br', 'www.convertpdf.com.br']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

