import subprocess

for line in open(".env"):
    subprocess.call("heroku config:set %s" % line.strip(), shell=True)