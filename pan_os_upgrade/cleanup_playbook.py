import glob, os
import logging.config
from logger_settings import logger_config
import re

logging.config.dictConfig(logger_config)
logger = logging.getLogger("cleanup")


def remove_arp_backup(workdir):
    logger.info("Removing ARP Backup Files")
    os.chdir(f"{workdir}/arp_backups")
    for filename in glob.glob("*.csv"):
        os.remove(filename)
    os.chdir(workdir)


def remove_host_var(workdir):
    store_pattern = re.compile(r"\d{4}\.yml")
    dir = f"{workdir}/host_vars"
    logger.info("Removing Host Vars Files")
    for rootdir, subdirs, filenames in os.walk(dir):
        for name in filenames:
            if store_pattern.search(name):
                file_name = os.path.join(rootdir, name)
                os.remove(file_name)


def remove_routing_backups(workdir):
    logger.info("Removing Routing Backups Files")
    os.chdir(f"{workdir}/routing_backups")
    for filename in glob.glob("*.csv"):
        os.remove(filename)
    os.chdir(workdir)


def clean_up_inventory_file(workdir):
    logger.info("Emptying Inventory File")
    os.chdir(workdir)
    open("inventory", "w").close()


def clean_up_ansible_log(workdir):
    logger.info("Emptying Ansible Log File")
    os.chdir(workdir)
    open("ansible_log.log", "w").close()


def main():
    workdir = os.getcwd()
    remove_arp_backup(workdir)
    remove_host_var(workdir)
    remove_routing_backups(workdir)
    clean_up_inventory_file(workdir)
    clean_up_ansible_log(workdir)


if __name__ == "__main__":
    main()
