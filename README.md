# nlp-ci

--------
Continue Integration (CI) for Natural Language Processing.

## Requirements
This script is tested on Ubuntu 14.04. It is recommended to use these scripts.

### Minimum requirements:
- apt-get
- git
- Python 2.7.6+
- Fabric 1.8.2+

### Extra requirements (if necessary for your case):
- Prepare SSL credentials.
- Define domain name of CI server.

## Installation
1. Prepare linux server.
1. Install git and Fabric.

  ```bash
  $ sudo apt-get -y -q install git fabric
  ```
  
1. Install and setup Jenkins server. 

  ```bash
  $ fab -u USERNAME -i PATH_TO_PRIVATE_KEY -H ADDRESS:22 install:domain=DOMAIN
  ```
  
  - USERNAME
    - An username to use when connecting to remote hosts.
  - PATH_TO_PRIVATE_KEY
    - A path to private key to use when connecting to remote hosts.
  - ADDRESS
    - An address of remote host for CI server.
  - DOMAIN
    - A domain of Jenkins page.
   
  If you want to install this system into local machine, `localhost` is set to `ADDRESS` variable.
  After successfully installing, you can access `https://ADDRESS/jenkins` as an `admin` user. (User name and password is same.)
  
  <!-- Insert figure about login image -->
  
1. Create job.
   ```bash
   $ fab -u USERNAME -i PATH_TO_PRIVATE_KEY -H ADDRESS:22 createjobs:domain=DOMAIN
   ```
   
  - USERNAME, PATH_TO_PRIVATE_KEY, ADDRESS, DOMAIN
    - Same as above step.
   
  Please see [joblist.json](docs/joblist.md). In current version, a test project for [jigg](https://github.com/mynlp/jigg.git) is already defined.
  
  The directory construction of `nlp-ci` is as follows:
  
  ```bash
  + nlp-ci
    +- INSTALL_SCRIPTS (fabfile.py, etc.)
    +- jigg (Base project)
    | +- Dockerfile
    | +- test.sh
    | +- jigg-develop (Target project directory1)
    | | +- src...
    | +- jigg-develop-other (Target project directory2)
    |   +- src...
    +- mecab
    | +- Dockerfile
    | +- test.sh
    | +- mecab-develop
    |   +- src...
    +- ...
  ```
   
1. Coding and push to the target repository.

1. Check result.

## Documents
1. [Install Jenkins using Fabric](docs/fabric.md)
1. [Job list](docs/joblist.md)
1. [Construction of project](docs/constructionOfProject.md)
1. [User authentication with OAuth plugin](docs/oauth.md)
1. [Plotting by each build job](docs/plot.md)
