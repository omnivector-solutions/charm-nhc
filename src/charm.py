#!/usr/bin/python3
"""NodeHealthCheckCharm"""
import copy
import logging
from pathlib import Path


from nhc_ops_manager import NhcOpsManager
from nhc_provides import NhcProvides
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    ModelError,
    WaitingStatus,
)


logger = logging.getLogger()

VERSION = '1.0.1'


class NhcCharm(CharmBase):
    """NhcCharm."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)

        self.unit.set_workload_version(VERSION)

        self._stored.set_default(
            slurm_info=dict()
        )

        self._nhc_provides = NhcProvides(self, "nhc")
        self._nhc_ops_manager = NhcOpsManager()

        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.update_status, self._on_update_status)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

        self.framework.observe(
            self._nhc_provides.on.slurm_info_available,
            self._on_slurm_info_changed
        )

        self.framework.observe(
            self._nhc_provides.on.update_relation_data,
            self._on_config_changed
        )

    def _on_install(self, event):
        nhc_snap_resource_path = None
        try:
            nhc_snap_resource_path = self.model.resources.fetch('nhc')
        except ModelError as e:
            logger.debug(f"Cannot find snap resource - {e}")

        if nhc_snap_resource_path is not None:
            msg = "Installing the NHC snap..."
            logger.debug(msg)
            self.unit.status = WaitingStatus(msg)
            self._nhc_ops_manager.install(nhc_snap_resource_path)
            Path(".installed").touch()
        else:
            self.unit.status = BlockedStatus(
                "Nhc snap resource not found!"
            )
            event.defer()

    def _on_update_status(self, event):
        self.unit.status = ActiveStatus("")

    def _on_config_changed(self, event):
        logging.debug('_on_config_changed(): entering')
        conf = self.model.config

        if not Path(".installed").exists():
            self.unit.status = WaitingStatus(
                "Waiting on nhc to finish installing..."
            )
            event.defer()
            return

        config_auto = conf['nhc-config-autodetect']
        logging.debug(f'_on_config_changed(): config_auto={config_auto}')
        
        # Write the nhc config
        self._nhc_ops_manager.write_nhc_config(config_auto, conf['nhc-config'])
        # Update relation data with config values if we are the leader
        if self.model.unit.is_leader():
            health_check_interval = conf['health-check-interval']
            health_check_node_state = conf['health-check-node-state']
            self._nhc_provides.update_relation_data(
                health_check_interval=health_check_interval,
                health_check_node_state=health_check_node_state,
            )

        self._nhc_ops_manager.set_nhc_debug(conf.get('debug'))
        self.unit.status = ActiveStatus("Config update complete")

    def _on_slurm_info_changed(self, event):
        if not Path(".installed").exists():
            event.defer()
            return

        slurm_info = copy.deepcopy(
            {k: v for k, v in self._stored.slurm_info.items()}
        )
        self._nhc_ops_manager.write_nhc_slurm_vars(slurm_info)

    def set_slurm_info(self, slurm_info):
        """Set slurm info."""
        self._stored.slurm_info = slurm_info


if __name__ == "__main__":
    main(NhcCharm)
