"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 4.1.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv  # Load environment variables
from neo4j import GraphDatabase
from neomodel import config

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = os.path.join(BASE_DIR, "myproject", ".env")
load_dotenv(ENV_PATH)

# Read from Render's environment variables (fallback to defaults for local development)
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://fa57a3a3.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mUB4QR3MrFW6x3OUeHiFlPI-WzTprL_P08DM9HiUFi8")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# Ensure the secret key is properly loaded
if not SECRET_KEY:
    raise ValueError("🚨 ERROR: DJANGO_SECRET_KEY is missing or not loaded correctly!")

import os

#print(os.environ)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://aunggyi:aung754826@cluster0.pim44.mongodb.net/yeryer")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "yeryer")

DEBUG=False


ALLOWED_HOSTS = ["*"]  # Change this to your domain or Render URL in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'main' / 'templates',
        ],
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

WSGI_APPLICATION = 'myproject.wsgi.application'

# Database Configuration (MongoDB)
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'yeryer',  # Replace with your actual DB name
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://aunggyi:aung754826@cluster0.pim44.mongodb.net/yeryer',
            'username': 'aunggyi',
            'password': 'aung754826',
            'authMechanism': 'SCRAM-SHA-1',
        }
    }
}




# -------------------------- Neo4j Configuration -------------------------------

# Initialize Neo4j Driver
def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Store in a variable so it can be used elsewhere
NEO4J_DRIVER = get_neo4j_driver()




# ----------------------------End of Neo4j Configuration ------------------------

# Maximum size for file uploads (e.g., 100MB)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = '/static/'

# Collect all static files into this directory when running collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Tell Django where to find additional static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main', 'static'),  # Add the existing static folder
]



# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL
LOGIN_URL = '/admin_login/'  # Replace with actual login path
