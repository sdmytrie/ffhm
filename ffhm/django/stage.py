"""
Config for production environment.
"""

from ffhm.env import env

from .base import *

DJANGO_DEBUG = env.bool("DJANGO_DEBUG", default=False)
CSRF_TRUSTED_ORIGINS = ["https://scoresheet.vps2.dmytrienko.com"]
