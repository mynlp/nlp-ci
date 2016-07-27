from time import sleep

from fabric.api import put, run, sudo, warn_only, hide, cd
from fabric.contrib.files import exists

import xml.etree.ElementTree as ET
import json

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
    sudo('apt-get -q update')
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

def _send_jenkins_cli_command(command, iterate = 100):
    count = 0
    with warn_only():
        result = sudo(command)
        with hide('everything'):
            while count < iterate and result.return_code != 0:
                result = sudo(command)
                if result.return_code != 0:
                    print 'Waiting for Jenkins-cli\'s response ...'
                    count += 1
                    sleep(1)
                else:
                    break

def install(username='admin', password='admin', domain=None, sslpath=None):
    # setup timezone
    sudo('echo Asia/Tokyo > /etc/timezone')
    sudo('dpkg-reconfigure --frontend noninteractive tzdata')

    # install apache2
    sudo('echo "export LANG=C" > /etc/profile')
    output = run('ifconfig eth0 | grep "inet addr:" | cut -d: -f2')
    privateIP = output.split(' ')[0].strip()
    address = domain

    _setup_apache2(address)

    # install required packages
    sudo('apt-get -q update')
    sudo('apt-get install -y -q openjdk-7-jre openjdk-7-jdk wget docker.io git maven')

    # install IPA font
    sudo('apt-get install -y -q fonts-ipafont-gothic fonts-ipafont-mincho')

    # install jenkins
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
                result = sudo('wget -nv --no-check-certificate -P /tmp/ https://%s/jenkins/jnlpJars/jenkins-cli.jar' % privateIP)
                if result.return_code != 0:
                    print 'Waiting for Jenkins to restart ...'
                    sleep(1)
                else:
                    break

    # add admin user
    _send_jenkins_cli_command('echo \'jenkins.model.Jenkins.instance.securityRealm.createAccount("%s","%s") \' \
    | java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s/jenkins groovy =' % (username, password, privateIP))

    # install plugins
    _send_jenkins_cli_command('java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s//jenkins install-plugin %s' % (privateIP,' '.join(plugins)))

    # deny access as anonymous
    sudo('/usr/local/bin/edit_jenkins_config /var/lib/jenkins/config.xml')

    # restart jenkins
    sudo('service jenkins restart')

    # copy test helper script
    put('run_test', '/tmp')
    sudo('mv /tmp/run_test /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/run_test')

    put('run_diff', '/tmp')
    sudo('mv /tmp/run_diff /usr/local/bin/.')
    sudo('chmod +x /usr/local/bin/run_diff')

    # copy whatswrong_command, which is a helper tool to compare files using whatswrong
    sudo('git clone https://github.com/mynlp/whatswrong_command.git /tmp/whatswrong_command')
    sudo('cd /tmp/whatswrong_command ; mvn assembly:assembly')
    sudo('mv /tmp/whatswrong_command//target/*.jar /usr/local/bin/.')

    # make data directory
    sudo('mkdir -p /data')

def createjobs(username='admin', password='admin', domain=None):

    if domain is None:
        sudo('echo "export LANG=C" > /etc/profile')
        output = run('ifconfig eth0 | grep "inet addr:" | cut -d: -f2')
        address = output.split(' ')[0].strip()
    else:
        address = domain

    f = open('./joblist.json')
    joblist = json.load(f)
    f.close()

    jobxml = ET.parse('./job-template.xml')
    jobxmlroot = jobxml.getroot()
    jobxmlnode = jobxmlroot.find('.//scms')

    nodetemplate = ET.parse('./node-template.xml')
    basenode = nodetemplate.findall('.//hudson.plugins.git.GitSCM')[0]
    testnode = nodetemplate.findall('.//hudson.plugins.git.GitSCM')[1]

    for elem in joblist:
        title = elem['.title']

        jobxmlnode.clear()

        basenode.find('.//url').text = elem['.contents']['base-project']['repository']
        basenode.find('.//name').text = '*/' + elem['.contents']['base-project']['branch']

        jobxmlnode.append(basenode)

        for subelem in elem['.contents']['test-projects']:
            testnode.find('.//url').text = subelem['repository']
            testnode.find('.//name').text = '*/' + subelem['branch']
            testnode.find('.//relativeTargetDir').text = title + '-' + subelem['branch']
            jobxmlnode.append(testnode)

        jobxml.write('./xml/%s.xml' % title, encoding='UTF-8')

        # create job
        put('./xml/%s.xml' % title, '/tmp/')
        _send_jenkins_cli_command(
            'cat /tmp/%s.xml | \
            java -jar /tmp/jenkins-cli.jar -noCertificateCheck -s https://%s/jenkins \
            create-job %s \
            --username %s \
            --password %s' % \
            (title, address, title, username, password))
