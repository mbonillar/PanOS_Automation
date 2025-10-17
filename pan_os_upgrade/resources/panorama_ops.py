import requests
from rich.console import Console
from urllib3.exceptions import InsecureRequestWarning
from panos.panorama import Panorama
from panos.device import SystemSettings


class PanoramaOperations:
    def __init__(self, ip_addr: str = ""):
        self.ip = ip_addr
        self.api_url = f"https://{self.ip}/api/"
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    def api_request(self, cmd: object) -> object:
        try:
            response = requests.get(f"{self.api_url}{cmd}", verify=False)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise SystemExit(err) from None

        return response.text

    def commit(self, api_key):
        cmd = f"?type=commit&cmd=<commit></commit>&key={api_key}"
        return self.api_request(cmd)

    def commit_and_push(self, api_key, device_group, template, serials):
        xml_devices = ["<devices>"]
        for serial in serials:
            xml_devices.append(f"entry name={serial}/>")
        xml_devices.append("</devices>")
        devices_xml_string = "".join(xml_devices)

        xpath = (
            f"<commit-and-push>"
            "<push-to>"
            "<shared-policy>"
            "<merge-with-candidate-cfg>yes</merge-with-candidate-cfg>"
            "<include-template>yes</include-template>"
            "<force-template-values>yes</force-template-values>"
            "<device-group>"
            f"<entry name={device_group}>"
            f"{devices_xml_string}"\
            "</entry>"
            "</device-group>"
            "</shared-policy>"
            "</push-to>"
            "</commit-and-push>"
        )
        cmd = f"?type=commit&cmd={xpath}&key={api_key}"
        return self.api_request(cmd)

    def export_template_variables(self, api_key, template_name="PaloAlto-Stores-Stack-V2"):
        element = '<request><operations xml="yes"><download><variable-config><name>PaloAlto-Stores-Stack-V2</name></variable-config></download></operations></request>'

        cmd = f"?type=op&cmd={element}&key={api_key}"
        return self.api_request(cmd)

    def export_device_inventory(self, api_key):
        cmd = f"?type=op&cmd=<show><devices><connected></connected></devices></show>&key={api_key}"
        return self.api_request(cmd)

    def show_high_vailability_status(self, api_key):
        cmd = f"?type=op&cmd=<show><high-availability><all></all></high-availability></show>&key={api_key}"
        return self.api_request(cmd)

    def revert_changes(self, api_key):
        cmd = f"?type=op&cmd=<revert><config><skip-validate>yes</skip-validate></config></revert>&key={api_key}"
        return self.api_request(cmd)
