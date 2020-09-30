#!/usr/bin/python3
"""NhcOpsManager."""
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger()


class NhcOpsManager:
    """NhcOpsManager."""

    def __init__(self):
        """Init class attributes."""
        self._nhc_config_path = Path(
            "/var/snap/nhc/common/etc/nhc/nhc.conf"
        )

        self._nhc_slurm_vars_path = Path(
            "/var/snap/nhc/common/vars/nhc_slurm_vars"
        )

        self._nhc_slurm_vars_template_path = Path(
            f"{os.getcwd()}/templates/nhc_slurm_vars"
        )

    def install(self, resource_path):
        """Install the nhc snap."""
        try:
            subprocess.call([
                "snap",
                "install",
                resource_path,
                "--dangerous",
                "--classic",
            ])
        except subprocess.CalledProcessError as e:
            print(f"Cannot install nhc- {e}")
            sys.exit(-1)

    def write_nhc_config(self, config_auto, nhc_config):
        """Write the nhc.conf."""
        if self._nhc_config_path.exists():
            self._nhc_config_path.unlink()

        if config_auto:
            cmd = """
(echo '* || HOSTNAME="$HOSTNAME_S"' &&
/snap/nhc/current/usr/sbin/nhc-genconf -c /dev/stdout \
INCDIR=/snap/nhc/current/usr/etc/nhc/scripts/ \
HELPERDIR=/var/snap/nhc/common/usr/lib/nhc | \
grep -v '/snap/') > %s""" % (str(self._nhc_config_path))

            logger.debug(f'write_nhc_config(): running "{cmd}"')
            os.system(cmd)
        else:
            self._nhc_config_path.write_text(nhc_config)

    def write_nhc_slurm_vars(self, slurm_info):
        """Write the slurm vars."""
        if self._nhc_slurm_vars_path.exists():
            self._nhc_slurm_vars_path.unlink()

        self._nhc_slurm_vars_path.write_text(
            self._nhc_slurm_vars_template_path.read_text().format(
                **slurm_info
            )
        )

    def set_nhc_debug(self, debug):
        """Set nhc debug logging."""
        nhc_debug = "false"
        if debug is True:
            nhc_debug = "true"
        subprocess.call([
            "snap",
            "set",
            "nhc",
            f"debug={nhc_debug}",
        ])
