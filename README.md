nlp-ci

======
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
  
1. Run fabfile.py using `fab` . 

  ```bash
  $ fab -u USERNAME -i PATH_TO_PRIVATE_KEY -H ADDRESS:22 install
  ```
  
  - USERNAME
    - username to use when connecting to remote hosts.
  - PATH_TO_PRIVATE_KEY
    - path to private key to use when connecting to remote hosts.
  - ADDRESS
    - address of remote host.
   
  If you want to install this system into local machine, `localhost` is set to `ADDRESS` variable.
  After successfully installing, you can access `https://ADDRESS/jenkins` as an `admin` user. (User name and password is same.)
  
  <!-- Insert figure about login situation -->
  
1. Create job.
   ```bash
   $ fab -u USERNAME -i PATH_TO_PRIVATE_KEY -H ADDRESS:22 createjobs
   ```
   
   Please see `joblist.json`. In current version, test project for [jigg](https://github.com/mynlp/jigg.git) is already defined.
   
1. Coding and push.

1. Check result.

## Documents
1. [Install Jenkins using Fabric](docs/fabric.md)
1. [Construction of project](docs/constructionOfProject.md)
1. [User authentication with OAuth plugin](docs/oauth.md)
1. [Plotting by each build job](docs/plot.md)

