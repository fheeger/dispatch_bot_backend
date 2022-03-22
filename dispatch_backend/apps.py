import subprocess

from django.apps import AppConfig


class BotConfig(AppConfig):
    name = 'dispatch_backend'

    def ready(self):
        subprocess.Popen(["python", "bot_script.py"])
