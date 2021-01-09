import os
from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False  # 꼭 필요합니다.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = secrets['ALLOWED_HOSTS']
DATABASES = secrets['DB_SETTINGS']


AWS_ACCESS_KEY_ID ='AKIAW5RH3VN4MCGEGL6L'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-northeast-2'

###S3 Storages
AWS_STORAGE_BUCKET_NAME = 'chatt-image-bucket' # 설정한 버킷 이름
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME,AWS_REGION)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

