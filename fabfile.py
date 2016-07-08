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
    ('plot', 'latest'),
	('github-oauth','latest'),
	('role-stragety','latest'),
]

# Setting apache
def _setup_apache2():
   sudo('apt-get -y -q install apache2')
   sudo('apache2ctl stop')
   sudo('sed -e \'/Listen/s/^/# /\' -i /etc/apache2/port.conf')
   sudo('a2enmod ssl')
   sudo('a2ensite default-ssl')
   sudo('a2enmod proxy')
   sudo('a2enmod proxy_http')
   sudo('a2enmod vhost_alias')
   sudo('apache2ctl start')

def _install_jenkins_plugin(name, version):
    sudo('wget -nv -P /var/lib/jenkins/plugins http://updates.jenkins-ci.org/download/plugins/%s/%s/%s.hpi' % (name, version, name))


def install():
    # setup timezone
    sudo('echo Asia/Tokyo > /etc/timezone')
    sudo('dpkg-reconfigure --frontend noninteractive tzdata')

    # install jenkins
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

    # install plugins
    for plugin, version in plugins:
        _install_jenkins_plugin(plugin, version)

	# add prefix option
	sudo('sed -e \'/JENKINS_ARGS/s/="/=" --prefix\/jenkins /\' -i /etc/default/jenkins')

    # restart jenkins
    sudo('service jenkins restart')

    # copy test helper script
    put('run_test', '/tmp')
    sudo('mv /tmp/run_test /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/run_test')

    put('run_diff', '/tmp')
    sudo('mv /tmp/run_diff /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/run_diff')

    # make data directory
    sudo('mkdir -p /data')

    # install apache2
    _setup_apache2()
