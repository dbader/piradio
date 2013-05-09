from fabric.api import env, hosts, sudo, local, settings, abort, run, cd
from fabric.contrib.console import confirm

PRODUCTION_SERVER = 'pi@piradio'
PRODUCTION_DIR = '/home/pi/piradio'
LOGFILES = ['/var/log/piradio.log']

def production():
   """ Use production server settings """
   env.hosts = [PRODUCTION_SERVER]
   env['dir'] = PRODUCTION_DIR

def deploy():
    with cd(env['dir']):
        run('git pull')
        run("find . -name '*.pyc' | xargs --no-run-if-empty rm")

def revert():
    """Revert git via reset --hard @{1}"""
    with cd(env['dir']):
        run('git reset --hard @{1}')

def start():
    sudo('service piradio start', pty=False)

def stop():
    sudo('service piradio stop', pty=False)

def restart():
    stop()
    start()

def logtail():
    run('tail %s' % ' '.join(LOGFILES))

def logfollow():
    run('tail -f %s' % ' '.join(LOGFILES))