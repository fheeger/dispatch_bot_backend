import subprocess
import os

from django.apps import AppConfig


class BotConfig(AppConfig):
    name = 'dispatch_backend'

    def ready(self):
        print("Startup hook for bot")
        if os.environ.get('RUN_MAIN'):
            subprocess.Popen("python bot_script.py", shell=True)
