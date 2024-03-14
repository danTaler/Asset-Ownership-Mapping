#! /usr/bin/env python3
import os
import logging
import sqlite3

from db import OpenStackDB
from db import Reports
from db.QualysDB import QualysDB

from sources.OpenStack import OpenStack
from sources.Qualys import Qualys
from destinations.GoogleSheet import GoogleSheet

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
)


def env_get(key):
    return (os.environ.get(key) or "").strip()


SERVICE = "openstack"
REPORT_DIR = os.environ.get("OPENSTACK_AUTOMATION_REPORT_DIR")
OPENSTACK_CLUSTERS = [
    {
        "env": "LAB",
        "url": "https://xxxxxxxxxxxxx",
        "username": env_get("OPENSTACK_IT_HYBRID_LAB_USERNAME"),
        "password": env_get("OPENSTACK_IT_HYBRID_LAB_PASSWORD"),
    },
    {
        "env": "PROD",
        "url": "https://xxxxxxxxxxxxxxx",
        "username": env_get("OPENSTACK_IT_HYBRID_PROD_USERNAME"),
        "password": env_get("OPENSTACK_IT_HYBRID_PROD_PASSWORD"),
    },
]
GOOGLE_SHEET_CONFIG = {
    "access": {
        # pylint: disable=line-too-long
        "sheet_url": "https://docs.google.com/spreadsheets/d/{xxxxxxxxxxxxxxxxxxx}/"
    },
    "reports": {
        "IT-Hybrid": {
            "header": "A1:R1",
            "rows": "A2:R9999",
            "id": "openstack_inventory_report",
        },
        # "IT-Infra": {
        #     "header": "A1:R1",
        #     "rows": "A2:R9999",
        #     "id": "TODO: add report to the Reports object"
        # },
    },
}


def main(db_path):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()

        # -- OpenStack ---
        logging.info("Starting Openstack")
        OpenStack(OpenStackDB(cur, con), OPENSTACK_CLUSTERS).sync()
        logging.info("Finished Openstack")

        # -- Qualys --
        logging.info("Starting Qualys")
        Qualys(QualysDB(cur, con), service=SERVICE).sync()
        logging.info("Finished Qualys")

        # -- Google Sheet --
        logging.info("Starting Update Google Sheets")
        GoogleSheet(Reports(cur, con), config=GOOGLE_SHEET_CONFIG).sync()
        logging.info("Finished Update Google Sheets")


if __name__ == "__main__":
    logging.info("Starting OpenStack Sync")

    if REPORT_DIR:
        if not os.path.exists(REPORT_DIR):
            os.makedirs(REPORT_DIR)

        SQLITE_DB_PATH = os.path.join(REPORT_DIR, "data-openstack.db")
    else:
        SQLITE_DB_PATH = ":memory:"

    main(SQLITE_DB_PATH)
    logging.info("Finished OpenStack/Qualys Sync")
