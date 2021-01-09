import os
from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False  # 꼭 필요합니다.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = secrets['ALLOWED_HOSTS']
DATABASES = secrets['DB_SETTINGS']

