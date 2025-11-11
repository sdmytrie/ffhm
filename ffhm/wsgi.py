"""
WSGI config for ffhm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from ffhm.env import BASE_DIR, env

env.read_env(os.path.join(BASE_DIR, ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ffhm.settings')

application = get_wsgi_application()
