# charm-nhc

### Introduction
A Juju subordinate charm for LBNL Node Health Check (NHC). Slurm is what actually runs NHC. Slurm has three NHC parameters in its `/etc/slurm/slurm.conf` (however for a snap-based setup of Slurm, the config file is located in `/var/snap/slurm/common/etc/slurm/slurm.conf`):

| Parameter            | Example value | Description                         |
|:---------------------|:--------------|:------------------------------------|
| HealthCheckProgram   | /snap/bin/nhc | Path to NHC                         |
| HealthCheckInterval  | 30            | Check frequency in seconds          |
| HealthCheckNodeState | ANY           | What node states should execute NHC |

### Build and install
```bash
charmcraft build --from ./charm-nhc

# A NHC snap
wget https://omnivector-public-assets.s3-us-west-2.amazonaws.com/snaps/nhc/edge/nhc_1.4.2-omni_amd64.snap -O nhc.snap

juju deploy nhc.charm --resource nhc=./nhc.snap
juju relate <primary charm> nhc
```

### Charm options
```bash
juju config nhc
```

| Setting&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Default | Description                                                                                                                                                                                                                                            |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| debug                                                                                                                                                                                 | false   |                                                                                                                                                                                                                                                        |
| health-check-interval                                                                                                                                                                 | 30      | See above                                                                                                                                                                                                                                              |
| health-check-node-state                                                                                                                                                               | ALL     | See above                                                                                                                                                                                                                                              |
| nhc-config                                                                                                                                                                            |         | A multi-line config string for NHC. Config options have the format: &#60;hostmask&#62; &#124;&#124; &#60;check&#62;. For example, &#60;hostmask&#62; can be * to run the check on all nodes or a specific hostname (other formats are also available). |
| nhc-config-auto                                                                                                                                                                       | true    | A boolean value indicating whether the config file should be autogenerated using `nhc-genconf` (anything in `nhc-config` will be ignored).                                                                                                             |

Default paths to the log and config files are `/var/snap/nhc/common/var/log/nhc/nhc.log` and `/var/snap/nhc/common/etc/nhc/nhc.conf`, respectively.

### Autogenerate a config file
```bash
/snap/nhc/current/usr/sbin/nhc-genconf -c ~/myconf.conf \
INCDIR=/snap/nhc/current/usr/etc/nhc/scripts/ \
HELPERDIR=/var/snap/nhc/common/usr/lib/nhc
```

### References
- https://github.com/mej/nhc
- https://slurm.schedmd.com/SUG14/node_health_check.pdf
- https://slurm.schedmd.com/slurm.conf.html

### Copyright
* Omnivector Solutions (c) 2020

### License
* MIT - see `LICENSE` file in this directory
