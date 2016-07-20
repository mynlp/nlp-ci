# Fabric

`fabfile.py` has two function, `install` and `createjobs`.

## install
### Arguments
- username 
  - User name of administrator for Jenkins. Default is `admin`.
- password 
  - Password of administrator. Default is `admin`.
- domain 
  - Domain name; if omitted, get from `ifconfig eth0`.
- sslpath (Not supported in latest version)
  - Path to SSL certification. 

### Workflow

1. Install apache2 and setup SSL networking.
1. Install required packages.
1. Install ipa fonts for drawing Japanese characters.
1. Install Jenkins.
1. Edit configuration of Jenkins and apply it.
1. Copy helper scripts.
1. Make a data directory.

## createjobs
### Arguments
- username
  - User name of administrator. Default is `admin`. 
- password
  - Password of administrator. Default is `admin`.
- domain
  - Domain name; if omitted, get from `ifconfig eth0`.

### Workflow
1. Load [`joblist.json`](docs/joblist.md).
1. Make job.xml.
1. Create job using jenkins-cli.jar.

## Plugins for Jenkins

You can define required plugins