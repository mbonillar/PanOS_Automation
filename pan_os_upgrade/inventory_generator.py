import click
import orionsdk
import requests
import json
import jinja2
import os
import sys
import logging.config
import xmltodict

from logger_settings import logger_config
from dotenv import load_dotenv
from icecream import ic
from resources.panos_api import ApiOps
from resources.panorama_ops import PanoramaOperations
from resources.panorama_ha import PanoramaHACheck


logging.config.dictConfig(logger_config)
logger = logging.getLogger("inventory_generator")

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def generate_api_key(panorama_ip_address, username, password):
    myapi = ApiOps(panorama_ip_address)
    api_key = myapi.generate_api_key(username, password)
    return api_key


def panorama_inventory(api_key, panorama_ip_address):
    """
    This function will extract panorama inventory.
    Parameters:
        prod: Boolean, True for production Panorama, False for LAB.
    """
    logger.info("Retrieving Panorama Firewalls Inventory")
    panorama_ops = PanoramaOperations(panorama_ip_address)
    xml_inventory = panorama_ops.export_device_inventory(api_key)

    try:
        inventory_dict = xmltodict.parse(xml_inventory)
    except Exception as err:
        logger.exception(f"Error retrieving Firewall Inventory from Panorama\n{err}")
        sys.exit(1)

    inventory = {}
    for dev in inventory_dict["response"]["result"]["devices"]["entry"]:
        inventory.update({dev["hostname"]: {}})
        inventory[dev["hostname"]].update({"serial": dev["serial"]})
        inventory[dev["hostname"]].update({"ip_address": dev["ip-address"]})
        try:
            inventory[dev["hostname"]].update({"state": dev["ha"]["state"]})
        except:
            inventory[dev["hostname"]].update({"state": ""})

    return inventory


def get_active_panorama(prod):
    logger.info("Check Active Panorama Controller IP Address")
    if prod:
        panorama_ip_address = "10.216.3.180"
    else:
        panorama_ip_address = "10.1.178.161"

    temp_panorama_ip_address = panorama_ip_address

    api_key = generate_api_key(
        panorama_ip_address, creds["pan_user"], creds["pan_pass"]
    )

    # return IP address of active Panorama in the HA pair.
    panorama_ip_address = PanoramaHACheck.verify_panorama_ha(
        panorama_ip_address, api_key
    )
    logger.info(f"Active Panorama Controller IP Address is: {panorama_ip_address}")
    # if Active Panorama IP is different then re-generate api_key using active IP address
    if temp_panorama_ip_address != panorama_ip_address:
        api_key = generate_api_key(
            panorama_ip_address, creds["pan_user"], creds["pan_pass"]
        )

    return api_key, panorama_ip_address


def group_stores(stores, inventory):
    """
    Group firewalls by store is a list of stores is passed.
    Parameters:
        inventory: dictionary of firewalls.
    Return:
        List of stores and firewalls in a dictionary.
    """

    store_mgmt = {}
    for store in stores:
        store_mgmt[store] = {}
        store_mgmt[store]["firewalls"] = {}
        for pan_fw in inventory:
            if store in pan_fw:
                store_mgmt[store]["firewalls"].update({pan_fw: inventory[pan_fw]})
    return store_mgmt


def execute_query(swis, query):
    # Execute the query
    try:
        results = swis.query(query)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Check if any devices were found
    if results["results"]:
        # Print details of the found devices
        return json.dumps(results["results"], indent=4)
    else:
        print("No devices found matching the criteria.")


def create_host_vars(store_mgmt):
    """
    Create host vars files for each store. This file will be used by Ansible to
    download and upgrade OS at the paloalto firewall for each store.
    :param nodes: dictionary containing the host ip information
    :return: Generate yml file and update Ansible inventory file.
    """
    with open("templates/host_vars_template.j2", "r") as jinja_config:
        config = jinja2.Template(jinja_config.read())
    for store in store_mgmt:
        file_name = f"host_vars/{store}.yml"
        for pan in store_mgmt[store]['firewalls']:
            fw_info = store_mgmt[store]['firewalls'][pan]
            if "fw1" in pan.lower():
                fw1_ip = fw_info['ip_address']
            if "fw2" in pan.lower():
                fw2_ip = fw_info['ip_address']
        logger.info(f"Creating file: {file_name}")
        with open(file_name, "w") as host_file:
            store_var = config.render({"fw1_ip_address": fw1_ip, "fw2_ip_address": fw2_ip})
            host_file.write(store_var)


def update_ansible_inventory(nodes):
    """
    Update Ansible inventory file with new stores
    :param nodes: dictionary with list of stores
    :return: Update Ansible inventory file
    """
    with open("inventory", "w") as ansible_inventory:
        for store in nodes:
            ansible_inventory.write(f"{store}\n")


@click.command()
@click.option("-s", "--store", help="Store(s) Number")
@click.option("-f", "--file", is_flag=True, help="Provide Store List in file")
@click.option("-p", "--prod", default=True, help="Production Panorama or LAB")
def ansible_inventory(store, file, prod):

    api_key, panorama_ip_address = get_active_panorama(prod)
    inventory = panorama_inventory(api_key, panorama_ip_address)

    if store:
        sites = store.split(",")
        # removing duplicate entries from sites
        stores_raw = set(sites)
    elif file:
        with open("store_list.txt", "r") as store_list:
            store = store_list.read()
        stores_raw = store.split('\n')
        stores_raw = set(stores_raw)
    else:
        logging.error("Please provide either a list of stores or a file name")
        sys.exit(1)

    stores = []
    for site in stores_raw:
        if site.rstrip():
            stores.append(site.strip())

    store_mgmt = group_stores(stores, inventory)

    logger.info("=> Updating Ansible Inventory File")
    update_ansible_inventory(stores)

    logger.info("=> Creating host vars yaml File for Stores Provided.")
    create_host_vars(store_mgmt)


@click.group()
@click.pass_context
def main(ctx):

    load_dotenv()

    ## global credentials dictionary to store information together
    global creds
    creds = {}

    # # environment variables are assigned as option to user
    if not os.getenv("pan_user"):
        logger.error("Environment variable 'pan_pass' not set.")
        sys.exit(1)
    else:
        creds["pan_user"] = os.getenv("pan_user")
        creds["pan_pass"] = os.getenv("pan_pass")


main.add_command(ansible_inventory)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Good Bye!")
        sys.exit(0)
