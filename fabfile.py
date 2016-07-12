from time import sleep

from fabric.api import put, run, sudo, warn_only, hide
from fabric.contrib.files import exists

# Jenkins plugins to install
plugins = [
    'scm-api',
    'git-client',
    'git',
    'ansicolor',
    'multiple-scms',
    'plot',
    'github-oauth',
    'role-strategy',
]

# setting apache
def _setup_apache2(address):
   sudo('apt-get -y -q install apache2')
   sudo('sed -e \'/Listen 80/s/^/# /\' -i /etc/apache2/ports.conf')
   sudo('a2enmod ssl')
   sudo('a2ensite default-ssl')
   sudo('a2enmod proxy')
   sudo('a2enmod proxy_http')
   sudo('a2enmod vhost_alias')
   put('default-ssl.conf','/tmp')
   sudo('sed -e "/{ADDRESS}/s/{ADDRESS}/%s/" -i /tmp/default-ssl.conf' % address)
   sudo('mv /etc/apache2/sites-available/default-ssl.conf /etc/apache2/sites-available-ssl.conf.backup')
   sudo('mv /tmp/default-ssl.conf /etc/apache2/sites-available/default-ssl.conf')
   sudo('apache2ctl restart')

def _install_jenkins_plugin(name, address):
    sudo('java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s//jenkins install-plugin %s' % (address, name))

def _check_jenkins_cli_status(address):
    with warn_only():
        with hide('everything'):
            while 1:
                result = sudo('java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s/jenkins help' % address)
                if result.return_code != 0:
                    print 'Waiting for Jenkins-cli to start ...'
                    sleep(1)
                else:
                    break

def install():
    # setup timezone
    sudo('echo Asia/Tokyo > /etc/timezone')
    sudo('dpkg-reconfigure --frontend noninteractive tzdata')

    # install apache2
    sudo('echo "export LANG=C" > /etc/profile')
    output = run('ifconfig eth0 | grep "inet addr:" | cut -d: -f2')
    address = output.split(' ')[0].strip()
    _setup_apache2(address)

    # install jenkins
    sudo('apt-get -q update')
    sudo('apt-get install -y -q openjdk-7-jre wget docker.io')
    run('wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -')
    sudo('sh -c \'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list\'')
    sudo('apt-get -q update')
    sudo('apt-get -y -q install jenkins')

    # add jenkins user to docker group to use docker in Jenkins
    sudo('gpasswd -a jenkins docker')

    # waiting jenkins to start
    while not exists('/var/lib/jenkins/config.xml'):
        print 'Waiting for Jenkins to start...'
        sleep(1)

    # add prefix option
    sudo('sed -e \'/JENKINS_ARGS/s/="/="--prefix=\/jenkins /\' -i /etc/default/jenkins')

    # Skip `unlock Jenkins`
    sudo('sed -e \'/JAVA_ARGS/s/="/="-Djenkins.install.runSetupWizard=false /\' -i /etc/default/jenkins')

    # edit configuration fow allowing anonymous to read jenkins configuration
    put('edit_jenkins_config','/tmp')
    sudo('mv /tmp/edit_jenkins_config /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/edit_jenkins_config')

    # allow access as anonymous
    sudo('/usr/local/bin/edit_jenkins_config --allowAnonymous /var/lib/jenkins/config.xml')

    # restart jenkins
    sudo('service jenkins restart')

    # download jenkins-cli
    with warn_only():
        with hide('everything'):
            while 1:
                result = sudo('wget -nv --no-check-certificate -P /tmp/ https://%s/jenkins/jnlpJars/jenkins-cli.jar' % address)
                if result.return_code != 0:
                    print 'Waiting for Jenkins to restart ...'
                    sleep(1)
                else:
                    break

    # add admin user
    _check_jenkins_cli_status(address)
    sudo('echo \'jenkins.model.Jenkins.instance.securityRealm.createAccount("admin","admin") \' \
    | java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s/jenkins groovy =' % address)

    # install plugins
    _check_jenkins_cli_status(address)
    sudo('java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s//jenkins install-plugin %s' % (address,' '.join(plugins)))

    # deny access as anonymous
    sudo('/usr/local/bin/edit_jenkins_config /var/lib/jenkins/config.xml')

    # reload configuration
    _check_jenkins_cli_status(address)
    sudo('java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s/jenkins reload-configuration' % address)

    # copy test helper script
    put('run_test', '/tmp')
    sudo('mv /tmp/run_test /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/run_test')

    put('run_diff', '/tmp')
    sudo('mv /tmp/run_diff /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/run_diff')

    # make data directory
    sudo('mkdir -p /data')

    # restart jenkins
    sudo('service jenkins restart')
