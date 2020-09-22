# charm-nhc

### Introduction
A subordinate charm for LBNL Node Health Check (NHC). Slurm is what actually runs NHC. Slurm has two NHC parameters in its `/etc/slurm/slurm.conf` (however for a snap-based setup of Slurm, the config file is located in `/var/snap/slurm/common/etc/slurm/slurm.conf`):

| Parameter            | Example value | Description                         |
|----------------------|---------------|-------------------------------------|
| HealthCheckProgram   | /snap/bin/nhc | Path to NHC.                        |
| HealthCheckInterval  | 30            | Check frequency in seconds.         |
| HealthCheckNodeState | ANY           | What node states should execute NHC |

### Build and install
```bash
charmcraft build --from ./charm-nhc

# A NHC snap
wget https://omnivector-public-assets.s3-us-west-2.amazonaws.com/snaps/nhc/edge/nhc_1.4.2-omni_amd64.snap -O nhc.snap
```

### References
- https://github.com/mej/nhc
- https://slurm.schedmd.com/SUG14/node_health_check.pdf

### Copyright
* Omnivector Solutions (c) 2020

### License
* MIT - see `LICENSE` file in this directory
