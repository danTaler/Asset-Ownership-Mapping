import os
import logging
import requests

from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from models.QualysAsset import QualysAsset


class QualysConnectionFailed(Exception):
    """
    This indicates that there was an issue communicating with Qualys
    """


class Qualys:
    _search_url = (
        "https://qualysapi.qg3.apps.qualys.com/qps/rest/2.0/search/am/hostasset"
    )

    _search_headers = {
        "X-Requested-With": "RH-Qualys-Automation",
        "Authorization": f"Basic {os.environ['QUALYS_CREDS_BASIC_AUTH']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self, db, service=None):
        self._db = db
        self._service = service

    def sync(self):
        self._db.reset()

        for asset in self._search_assets(self._service):
            self._db.insert_asset(asset)

    @property
    def _searches(self):
        """
        Return a new dict each time so that we can mutate it freely
        """
        return {
            "aws": {
                "fields": (
                    "id",
                    "name",
                    "created",
                    "sourceInfo.list.Ec2AssetSourceSimple.instanceId",
                    "agentInfo.lastCheckedIn",
                    "agentInfo.status",
                ),
                "payload": {
                    "ServiceRequest": {
                        "filters": {
                            "Criteria": [
                                {
                                    "field": "cloudProviderType",
                                    "operator": "EQUALS",
                                    "value": "AWS",
                                },
                            ],
                        },
                        "preferences": {
                            "limitResults": "500",
                        },
                    },
                },
            },
            "openstack": {
                "fields": (
                    "agentInfo.status",
                    "agentInfo.lastCheckedIn",
                    "fqdn",
                    "qwebHostId",
                    "os",
                    "address",
                    "networkInterface",
                ),
                "payload": {
                    "ServiceRequest": {
                        "filters": {
                            "Criteria": [
                                {
                                    "field": "tagId",
                                    "operator": "EQUALS",
                                    "value": "xxxxxxxxxxxxxxxxx",
                                },
                            ],
                        },
                        "preferences": {
                            "limitResults": "500",
                        },
                    },
                },
            },
        }

    @staticmethod
    def _retryable_session():
        """
        HTTP request for retries (it keeps fails against Qualys HTTPS)
        """
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
            )
        )

        session = requests.Session()
        session.mount("https://", adapter)

        return session

    def _search_assets(self, service):
        """
        Lookup qualys assets
        """
        logging.info("Fetching Qualys Assets")
        has_more_records = True
        last_id = None

        while has_more_records:
            # Note: self._searches should be a property that generates the
            # search_config new each time so that we can mutate it freely
            search_config = self._searches[service]
            fields = search_config["fields"]
            payload = search_config["payload"]

            if last_id:
                payload["ServiceRequest"]["filters"]["Criteria"].append(
                    {
                        "field": "id",
                        "operator": "GREATER",
                        "value": str(last_id),
                    },
                )

            with self._retryable_session() as session:
                resp_json = session.post(
                    f"{self._search_url}?fields={','.join(fields)}",
                    headers=self._search_headers,
                    json=payload,
                    timeout=600,
                ).json()

            if resp_json["ServiceResponse"]["responseCode"] != "SUCCESS":
                raise QualysConnectionFailed(
                    f"Could not contact Qualys: {resp_json['ServiceResponse']}"
                )

            has_more_records = (
                resp_json["ServiceResponse"].get("hasMoreRecords") == "true"
            )
            last_id = resp_json["ServiceResponse"].get("lastId")

            if has_more_records:
                logging.info("Will start another lookup with id > %s", last_id)

            for host in resp_json["ServiceResponse"].get("data", []):
                asset = host["HostAsset"]
                source_info_list = (asset.get("sourceInfo") or {}).get("list") or []
                aws_instance_id = ""

                for item in source_info_list:
                    if "Ec2AssetSourceSimple" in item:
                        aws_instance_id = (
                            item["Ec2AssetSourceSimple"].get("instanceId") or ""
                        )
                        break

                yield QualysAsset(
                    id=asset.get("id") or 0,
                    name=asset.get("name"),
                    agent_status=asset.get("agentInfo", {}).get("status") or "",
                    aws_instance_id=aws_instance_id,
                    fqdn=asset.get("fqdn") or "",
                    ip_address=asset.get("address") or "",
                    last_checked_in=asset.get("agentInfo", {}).get("lastCheckedIn") or "",
                    os=asset.get("os") or "",
                    qweb_host_id=asset.get("qwebHostId") or 0,
                )
