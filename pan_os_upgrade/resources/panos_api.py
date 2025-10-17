import requests
import xml.etree.ElementTree as ET
from urllib3.exceptions import InsecureRequestWarning


class ApiOps:
    def __init__(self, mgmt_ip):
        self.ip = mgmt_ip
        self.api_url = f"https://{self.ip}/api/"
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    def api_request(self, cmd: object) -> object:
        try:
            response = requests.get(self.api_url + cmd, verify=False)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise SystemExit(err) from None

        return response.text

    def api_request_no_error_check(self, cmd: object) -> str:
        response = requests.get(self.api_url + cmd, verify=False)
        return response.text

    def generate_api_key(self, user: str, password: str) -> str:
        cmd = f"?type=keygen&user={user}&password={password}"
        string_response: object = self.api_request(cmd)
        xml_response = ET.fromstring(string_response)
        api_key: str | None = xml_response.findall("result/key")[0].text

        return api_key
