# inventory_parser.py

import xmltodict
import sys
import logging
from rich.logging import RichHandler

from .panorama_ops import PanoramaOperations

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(show_path=True)],
)
logger = logging.getLogger(__name__)


class PanoramaHACheck:

    @classmethod
    def verify_panorama_ha(cls, panorama_ip_address, api_key):
        """
        Verifies in Production, which Panorama Controller is active and return its IP address.
        :param api_key: token generated to access API
        :return: ip-address of active panorama controller.
        """
        ha_info = PanoramaOperations(panorama_ip_address)
        ha_status = ha_info.show_high_vailability_status(api_key)
        ha_status_parsed = xmltodict.parse(ha_status)

        try:
            enabled = ha_status_parsed["response"]["result"]["enabled"]
        except KeyError as err:
            logger.error(f"I am not able to retrieve Panorama information: {err}")
            sys.exit(1)

        # return Panorama IP address if not in HA mode and only a single Panorama
        # controller. Example: Lab Panorama
        if enabled == "no":
            return panorama_ip_address

        local_ha_status = None
        peer_ha_status = None
        try:
            local_ha_status = ha_status_parsed["response"]["result"]["local-info"]["state"]
        except KeyError as err:
            logger.error(f"Not able to retrieve Primary Panorama Information: {err}")
        try:
            peer_ha_status = ha_status_parsed["response"]["result"]["peer-info"]["state"]
        except KeyError as err:
            logger.error(f"Not able to retrieve Secondary Panorama Information: {err}")

        if local_ha_status:
            if local_ha_status == "primary-active":
                panorama_ip_address = ha_status_parsed["response"]["result"]["local-info"][
                    "mgmt-ip"
                ].split("/")[0]
                logger.info(f"{panorama_ip_address} - {local_ha_status}")
            elif local_ha_status == "primary-passive":
                pass

        if peer_ha_status:
            if peer_ha_status == "secondary-active":
                panorama_ip_address = ha_status_parsed["response"]["result"]["local-info"][
                    "mgmt-ip"
                ].split("/")[0]
                logger.info(f"{panorama_ip_address} - {peer_ha_status}")
            elif local_ha_status == "secondary-passive":
                pass
        logger.info(panorama_ip_address)
        return panorama_ip_address
