import csv
from collections import defaultdict


def check_row(row):

    if row['HA_Active_Status'].strip() == 'active' and row['HA_Passive_Status'].strip() == 'passive':
        ha_ok = True
    else:
        ha_ok = False

    if row['FW1_Pre_OS'] == row['FW1_Pos_OS']:
        fw1_upgrade_status = 'Failed'
        fw1_upgrade_ok = False
    else:
        fw1_upgrade_ok = 'Success'
        upgrade_ok = True

    if row['FW2_Pre_OS'] == row['FW2_Pos_OS']:
        fw2_upgrade_status = 'Failed'
        fw2_upgrade_ok = False
    else:
        fw2_upgrade_ok = 'Success'
        upgrade_ok = True

    if row['BGP_State'].strip() == 'Established':
        bgp_ok = True
    else:
        bgp_ok = False
    if int(row['Sessions_Post_SSL']) > 0:
        ssl_ok = True
    else:
        ssl_ok = False
    if int(row['Sessions_Post_DNS']) > 0:
        dns_ok = True
    else:
        dns_ok = False
    if int(row['Sessions_Post_LDAP']) > 0:
        ldap_ok = True
    else:
        ldap_ok = False
        print("FAILED")
        print(f"Session Post LDAP: {row['Sessions_Post_LDAP']}")

    if all([ha_ok, bgp_ok, ssl_ok, dns_ok, ldap_ok, upgrade_ok]):
        msg = False
    else:
        msg = f"Store: {row['Store_Number']} needs some attention."
        if fw1_upgrade_status == 'Failed' or fw2_upgrade_status == 'Failed':
            msg += " Upgrade Failed."
        if not ha_ok:
            msg += " Found HA Issues."
        if not bgp_ok:
            msg += " Found BGP Issues."
        if not ssl_ok:
            msg += " Found SSL Issues."
        if not ldap_ok:
            msg += " Found LDAP Issues."
    return msg


class FilterModule(object):
    """
    Filter Module to count number of active sessions
    """
    def filters(self):
        return {
            'active_sessions': self.sessions,
            'arp_backups': self.write_arp_csv,
            'routing_backups': self.write_routing_csv,
            'audit_csv': self.audit_csv_file
        }

    def sessions(self, sessions: dict) -> dict:

        active_sessions = defaultdict(int)
        if not isinstance(sessions, dict):
            # return False if Sessions is not a dictionary
            return

        try:
            # using default values if none of the apps is found
            active_sessions["ssl"] = 0
            active_sessions["dns_base"] = 0
            active_sessions["ldap"] = 0
            for app in sessions["response"]["result"]["entry"]:
                if 'ssl' in app["application"]:
                    active_sessions["ssl"] += 1
                if 'dns' in app["application"]:
                    active_sessions["dns_base"] += 1
                if 'ldap' in app["application"]:
                    active_sessions["ldap"] += 1
        except KeyError:
            # return false if there's a Key Error
            return

        # successful return sessions
        return dict(active_sessions)

    def write_arp_csv(self, arp_json, store, capture_type):
        if capture_type == "pre":
            file_name = f"arp_backups/{store}_pre_arp_backup.csv"
        if capture_type == "post":
            file_name = f"arp_backups/{store}_post_arp_backup.csv"
        try:
            with open(file_name, "w", newline="") as new_csv:
                csv_writer = csv.writer(new_csv, delimiter=",")
                csv_writer.writerow(["Interface", "IP_Address", "MAC_Address"])
                for arp_entry in arp_json["response"]["result"]["entries"]["entry"]:
                    csv_writer.writerow([arp_entry['interface'], arp_entry['ip'], arp_entry['mac']])
        except (FileNotFoundError, PermissionError, OSError):
            return {"result": False, "filename": file_name}

        return {"result": False, "filename": file_name}

    def write_routing_csv(self, routing, store, capture_type):
        if capture_type == "pre":
            file_name = f"routing_backups/{store}_pre_routing_backup.csv"
        if capture_type == "post":
            file_name = f"routing_backups/{store}_post_routing_backup.csv"

        try:
            with open(file_name, "w", newline="") as new_csv:
                csv_writer = csv.writer(new_csv, delimiter=",")
                csv_writer.writerow(["Destination", "Next_Hop", "Metric", "Flags", "Age", "Interface"])
                for entry in routing['response']['result']['entry']:
                    csv_writer.writerow([entry['destination'],
                                         entry['nexthop'],
                                         entry['metric'],
                                         entry['flags'],
                                         entry['age'],
                                         entry['interface']
                                         ])
        except (FileNotFoundError, PermissionError, OSError):
            return {"result": False, "filename": file_name}

        return {"result": True, "filename": file_name}

    def audit_csv_file(self, csv_file: object) -> dict:
        """
        :param csv_file: this file is generated by ansible-playbook.
        :return: a dictionary with a list of messages. Each item in the list
        is a store with issues or a single message with successful upgrade if
        no errors were found.
        """
        file_name = f"reports/{csv_file}"

        with open(file_name, newline='') as csv_file:
            report_reader = csv.DictReader(csv_file)
            stores = 0
            msg = []
            for line in report_reader:
                stores += 1
                issues = check_row(line)
                if issues:
                    msg.append(issues)
            if len(msg) == 0:
                msg.append(f"Upgraded {stores} stores Successfully.")
        return msg