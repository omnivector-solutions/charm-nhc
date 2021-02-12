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

juju deploy ./nhc.charm --resource nhc=./nhc.snap
juju relate slurmd nhc
juju relate slurm-configurator nhc
```

### Charm options
```bash
juju config nhc
```

| Setting                  | Default | Description                                                                                                                                                                                                                |
|:-------------------------|:--------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| debug                    | false   |                                                                                                                                                                                                                            |
| health-check-interval    | 30      | See above                                                                                                                                                                                                                  |
| health-check-node-state  | ALL     | See above                                                                                                                                                                                                                  |
| nhc-config               |         | A multi-line config string for NHC. Config options have the format: `<hostmask> || <check>`. For example, `<hostmask>` can be `*` to run the check on all nodes or a specific hostname (other formats are also available). |

Default paths to the log and config files are `/var/snap/nhc/common/var/log/nhc/nhc.log` and `/var/snap/nhc/common/etc/nhc/nhc.conf`, respectively.

### Autogenerate a config file
The below command is just to show how the charm generates the config file. Rules containing /snap/ and /run/user paths are removed, because they give failures too often.
```bash
/snap/nhc/current/usr/sbin/nhc-genconf -c /dev/stdout \
INCDIR=/snap/nhc/current/usr/etc/nhc/scripts/ \
HELPERDIR=/var/snap/nhc/common/usr/lib/nhc | grep -v '/snap/' | \
grep -v '/run/user/' > ~/myconf.conf
```

### _Important_ change to the NHC configuration file
We need to add `* || HOSTNAME="$HOSTNAME_S"` to the top of `nhc.conf` because otherwise there will be a mismatch between the hostname that NHC picks from `/proc/sys/kernel/hostname` and the shorter version used by slurm. The issue is discussed [here](https://github.com/mej/nhc/issues/19) and [here](https://github.com/mej/nhc/issues/19), and the messages we don't want to see `nhc.log` are the following:

```
/var/snap/nhc/common/usr/lib/nhc/node-mark-online:  Not sure how to handle node state "" on foobar.mydomain.com
/var/snap/nhc/common/usr/lib/nhc/node-mark-online:  Skipping  node foobar.mydomain.com ( )
```

### References
- https://github.com/mej/nhc
- https://slurm.schedmd.com/SUG14/node_health_check.pdf
- https://slurm.schedmd.com/slurm.conf.html

### Copyright
* Omnivector Solutions (c) 2020

### License
* MIT - see `LICENSE` file in this directory
