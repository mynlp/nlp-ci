from time import sleep

from fabric.api import put, run, sudo
from fabric.contrib.files import exists

# Jenkins plugins to install
plugins = [
    ('scm-api', 'latest'),
    ('git-client', 'latest'),
    ('git', 'latest'),
    ('ansicolor', 'latest'),
    ('multiple-scms', 'latest'),
]


def _install_jenkins_plugin(name, version):
    sudo('wget -nv -P /var/lib/jenkins/plugins http://updates.jenkins-ci.org/download/plugins/%s/%s/%s.hpi' % (name, version, name))


def install():
    # setup timezone
    sudo('echo Asia/Tokyo > /etc/timezone')
    sudo('dpkg-reconfigure --frontend noninteractive tzdata')

    # install jenins
    sudo('apt-get -q update')
    sudo('apt-get install -y -q openjdk-7-jre wget docker.io')
    run('wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -')
    sudo('sh -c \'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list\'')
    sudo('apt-get -q update')
    sudo('apt-get -y -q install jenkins')

    while not exists('/var/lib/jenkins/plugins'):
        print 'Waiting for Jenkins to start...'
        sleep(1)

    # add jenkins user to docker group to use docker in Jenkins
    sudo('gpasswd -a jenkins docker')

    for plugin, version in plugins:
        _install_jenkins_plugin(plugin, version)