#!/usr/bin/python3
"""SlurmctldCharm."""
import copy


from nhc_ops_manager import NhcOpsManager
from nhc_provides import NhcProvides
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    ModelError,
)


class NhcCharm(CharmBase):
    """NhcCharm."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)

        self._stored.set_default(
            nhc_installed=False,
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
        try:
            nhc_snap_resource_path = self.model.resources.fetch('nhc')
        except ModelError as e:
            print(f"Cannot find resource - {e}")
            nhc_snap_resource_path = None

        if nhc_snap_resource_path is not None:
            self._nhc_ops_manager.install(nhc_snap_resource_path)
            self._stored.nhc_installed = True
            self.unit.status = ActiveStatus("NHC installed")
        else:
            self.unit.status = BlockedStatus(
                "Nhc snap resource not found!"
            )
            event.defer()

    def _on_update_status(self, event):
        self.unit.status = ActiveStatus("")

    def _on_config_changed(self, event):
        conf = self.model.config

        if not self._stored.nhc_installed:
            event.defer()
            return

        # Write the nhc config
        self._nhc_ops_manager.write_nhc_config(conf['nhc-config'])
        # Update relation data with config values if we are the leader
        if self.model.unit.is_leader():
            health_check_interval = conf['health-check-interval']
            health_check_node_state = conf['health-check-node-state']
            self._nhc_provides.update_relation_data(
                health_check_interval=health_check_interval,
                health_check_node_state=health_check_node_state,
            )

        self._nhc_ops_manager.set_nhc_debug(conf.get('debug'))

    def _on_slurm_info_changed(self, event):
        if not self._stored.nhc_installed:
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
