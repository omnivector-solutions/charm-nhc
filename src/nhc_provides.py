#!/usr/bin/python3
"""NHC Provides."""
import logging
from ops.framework import (
    EventBase,
    EventSource,
    Object,
    ObjectEvents,
)

logger = logging.getLogger()


class SlurmInfoAvailableEvent(EventBase):
    """Emmited when slurm relation info is available."""


class UpdateRelationDataEvent(EventBase):
    """Emmited when an update to relation data is needed."""


class NhcEvents(ObjectEvents):
    """NhcEvents."""

    slurm_info_available = EventSource(SlurmInfoAvailableEvent)
    update_relation_data = EventSource(UpdateRelationDataEvent)


class NhcProvides(Object):
    """NhcProvides."""

    on = NhcEvents()

    def __init__(self, charm, relation):
        """Set the initial values."""
        super().__init__(charm, relation)
        self._charm = charm
        self._relation_name = relation
        self._nhc_bin = "/snap/bin/nhc"

        self.framework.observe(
            self._charm.on[self._relation_name].relation_created,
            self._on_relation_created
        )
        self.framework.observe(
            self._charm.on[self._relation_name].relation_changed,
            self._on_relation_changed
        )

    @property
    def _relation(self):
        return self.framework.model.get_relation(self._relation_name)

    def _on_relation_created(self, event):
        if self.framework.model.unit.is_leader():
            self.on.update_relation_data.emit()

    def _on_relation_changed(self, event):
        if not event.relation.data.get(event.app):
            event.defer()
            return

        app_data = event.relation.data[event.app]
        sinfo = app_data.get('sinfo')
        scontrol = app_data.get('scontrol')
        slurm_conf = app_data.get('slurm_conf')

        if sinfo and scontrol and slurm_conf:
            self._charm.set_slurm_info({
                'sinfo': sinfo,
                'scontrol': scontrol,
                'slurm_conf': slurm_conf,
            })
            self.on.slurm_info_available.emit()

    def update_relation_data(self,
                             health_check_interval, health_check_node_state):
        """Update the relation data."""
        app = self.model.app
        app_data = self._relation.data[app]

        app_data['nhc_bin'] = self._nhc_bin
        app_data['health_check_interval'] = health_check_interval
        app_data['health_check_node_state'] = health_check_node_state
