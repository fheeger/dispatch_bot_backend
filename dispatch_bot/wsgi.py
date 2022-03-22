"""
WSGI config for dispatch_bot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import subprocess

from django.core.wsgi import get_wsgi_application

subprocess.Popen(["python", "bot_script.py"])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dispatch_bot.settings')

application = get_wsgi_application()
