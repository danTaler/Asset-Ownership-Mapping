import os
import logging

from subprocess import check_output  # nosec
from ipaddress import IPv4Network
from defusedxml import ElementTree as ET
from models.NmapResultsEntry import NmapResultsEntry


class NmapScans:
    def __init__(self, db, datacenters):
        self._db = db
        self._datacenters = datacenters

    def sync(self):
        self._db.reset()

        for datacenter in self._datacenters:
            self.scan(datacenter)

    def scan(self, datacenter):
        """
        Nmap has the ability to port scan or version scan multiple hosts in
        parallel

        Nmap does this by dividing the target IP space into groups and then
        scanning one group at a time.

        In general, larger groups are more efficient.

        The downside is that host results can't be provided until
        the whole group is finished.
        (except for the updates offered in verbose mode)
        """
        net = IPv4Network(datacenter["ip_range"])
        for target in net.subnets(new_prefix=29):
            try:
                logging.info("Nmap Scan Started datacenter=%s", datacenter["name"])
                nmap_path = "/usr/bin/nmap"
                if not os.path.exists(nmap_path):
                    nmap_path = "/usr/local/bin/nmap"

                raw_results = check_output(  # nosec
                    [
                        "/usr/bin/sudo",
                        nmap_path,
                        "-oX",
                        "-",
                        "-v",
                        "-sS",
                        str(target),
                    ],
                    shell=False,
                )

                self.save_hosts(datacenter, ET.fromstring(raw_results).findall("host"))
                logging.info("Nmap Scan Finished datacenter=%s", datacenter["name"])
            except Exception as e:
                logging.error("Nmap Scan Failed error=%s", e)

    def save_hosts(self, datacenter, hosts):
        for host in hosts:
            if host.find("status").attrib["state"] != "up":
                continue

            nmap_results = NmapResultsEntry(
                datacenter=datacenter["name"],
                public_ip=host.find("address").attrib["addr"],
                hostname=host.find("hostnames").find("hostname").attrib["name"],
                ports=[
                    port.attrib["portid"]
                    for port in host.find("ports").findall("port")
                    if port.find("state").attrib["state"] == "open"
                ],
            )

            if nmap_results.ports:
                self._db.insert_nmap_results(nmap_results)
