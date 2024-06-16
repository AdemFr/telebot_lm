import logging

from googleapiclient import discovery

logger = logging.getLogger(__name__)


class GCPInstanceHandler:
    def __init__(self, project, zone, service_name):
        self.project = project
        self.zone = zone
        self.service_name = service_name
        self._service = discovery.build("compute", "v1")

    def start_instance(self):
        try:
            logger.info("VM Instance starting")
            self._service.instances().start(
                project=self.project, zone=self.zone, instance=self.service_name
            ).execute()
            logger.info("VM Instance started")
            return "VM Instance started"
        except Exception as e:
            logger.error(f"Failed to start VM Instance: {e}")
            return "Failed to start VM Instance"

    def stop_instance(self):
        try:
            logger.info("VM Instance stopping")
            self._service.instances().stop(
                project=self.project, zone=self.zone, instance=self.service_name
            ).execute()
            logger.info("VM Instance stopped")
            return "VM Instance stopped"
        except Exception as e:
            logger.error(f"Failed to stop VM Instance: {e}")
            return "Failed to stop VM Instance"

    def get_status(self):
        try:
            logger.info("Getting status of VM Instance")
            instance = (
                self._service.instances()
                .get(project=self.project, zone=self.zone, instance=self.service_name)
                .execute()
            )
            return instance["status"]
        except Exception as e:
            logger.error(f"Failed to get status of VM Instance: {e}")
            return "Failed to get status of VM Instance"
