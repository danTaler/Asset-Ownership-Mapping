import logging

import requests

from models.OpenStackServer import OpenStackServer
from models.OpenStackProject import OpenStackProject


class OpenStack:
    def __init__(self, db, clusters):
        self._db = db
        self._clusters = clusters

    def sync(self):
        """
        Reset the DB tables
        """
        self._db.reset()

        for cluster in self._clusters:
            cluster_auth_token = self._get_auth_token(cluster)

            if not cluster_auth_token:
                logging.warning("Skipping cluster=%s", cluster["url"])
                continue

            for project in self._fetch_projects(cluster, cluster_auth_token):
                self._db.insert_project(project)

                project_auth_token = self._get_auth_token(cluster, project)

                if not project_auth_token:
                    logging.warning(
                        "Skipping project=%s on cluster=%s",
                        project.name,
                        cluster["url"],
                    )
                    continue

                servers = self._fetch_servers(cluster, project, project_auth_token)

                for server in servers:
                    self._db.insert_server(server)

    def _get_auth_token(self, cluster, project=None):
        """
        Auth: get new auth token per scoped project and same domain ID
        """
        logging.info(
            "Getting auth token for cluster=%s project=%s",
            cluster["url"],
            project.name if project else "",
        )

        request_body = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": cluster["username"],
                            "domain": {"name": "default"},
                            "password": cluster["password"],
                        }
                    },
                }
            }
        }

        if project:
            request_body["auth"]["scope"] = {
                "project": {
                    "name": project.name,
                    "domain": {
                        "id": project.domain_id,
                    },
                }
            }

        response = requests.post(
            f"{cluster['url']}:13000/v3/auth/tokens",
            json=request_body,
            timeout=30,
            headers={
                "Content-Type": "application/json",
            },
        )

        try:
            response.raise_for_status()
            return response.headers["X-Subject-Token"]
        except Exception as e:
            logging.exception(e)
            return None

    def _fetch_projects(self, cluster, auth_token):
        """
        return list of all projects
        """
        logging.info("Fetching projects: cluster=%s", cluster["url"])
        response = requests.get(
            f"{cluster['url']}:13000/v3/auth/projects",
            timeout=30,
            headers={
                "X-Auth-Token": auth_token,
                "Content-Type": "application/json",
            },
        )

        # This needs to check for pagination. It currently doesn't.
        for project in response.json()["projects"]:
            yield OpenStackProject(
                id=project.get("id") or "",
                name=project.get("name") or "",
                description=project.get("description") or "",
                tags=project.get("tags") or "",
                enable=project.get("enabled") or "",
                domain_id=project.get("domain_id") or "",
            )

    def _fetch_servers(self, cluster, project, auth_token):
        """
        Get the servers per project scope
        """
        logging.info(
            "Fetching servers for cluster=%s project=%s",
            cluster["url"],
            project.name if project else "",
        )

        response = requests.get(
            f"{cluster['url']}:13774/v2.1/servers/detail",
            timeout=30,
            headers={
                "X-Auth-Token": auth_token,
                "Content-Type": "application/json",
            },
        )

        for server in response.json()["servers"]:
            metadata = server.get("metadata") or {}
            ip_address_1 = ""

            parent_tag_ip_addresses = server.get("addresses")
            if parent_tag_ip_addresses.values():
                address_tag = list(parent_tag_ip_addresses.values())[0]

            if len(address_tag) > 1:
                ip_address_1 = address_tag[1]["addr"]

            yield OpenStackServer(
                env=cluster["env"],
                id=server.get("id") or "",
                name=server.get("name") or "",
                status=server.get("status") or "",
                created=server.get("created") or "",
                project=project,
                metadata_hostname=metadata.get("HostName") or "",
                metadata_owner=metadata.get("ServiceOwner") or "",
                metadata_appcode=metadata.get("AppCode") or "",
                ip_address_access=server.get("accessIPv4") or "",
                ip_address_0=(address_tag[0] or {}).get("addr") or "",
                ip_address_1=ip_address_1,
                # TO DO: "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:e9:5d:ef"
                # mac_address = addr[0]['addr']
            )
