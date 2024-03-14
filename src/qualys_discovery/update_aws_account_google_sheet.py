#! /usr/bin/env python3
import os
import logging
import sqlite3

from db import AwsDB
from db import QualysDB
from db import Reports

from sources.Aws import Aws
from sources.Qualys import Qualys
from destinations.GoogleSheet import GoogleSheet

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
)

REPORT_DIR = os.environ.get("QUALYS_AUTOMATION_REPORT_DIR")

SERVICE = "aws"

GOOGLE_SHEET_CONFIG = {
    "access": {
        # pylint: disable=line-too-long
        "sheet_url": "https://docs.google.com/spreadsheets/d{xxxxxxxxxxxxxxx}/",
    },
    "reports": {
        "Accounts": {
            "id": "aws_accounts_report",
            "header": "A1:H1",
            "rows": "A2:H9999",
        },
        "Inventory": {
            "id": "aws_inventory_report",
            "header": "A1:X1",
            "rows": "A2:X9999",
        },
    },
}


def main(db_path):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()

        # -- AWS --
        logging.info("Starting Query AWS records")
        Aws(AwsDB(cur, con)).sync()
        logging.info("Finished Query AWS records")

        # -- Qualys --
        logging.info("Starting Query Qualys records")
        Qualys(QualysDB(cur, con), service=SERVICE).sync()
        logging.info("Finished Query Qualys records")

        # -- Google Sheet --
        logging.info("Starting Update Google Sheets")
        GoogleSheet(Reports(cur, con), config=GOOGLE_SHEET_CONFIG).sync()
        logging.info("Finished Update Google Sheets")


if __name__ == "__main__":
    logging.info("Starting AWS/Qualys Sync")

    if REPORT_DIR:
        if not os.path.exists(REPORT_DIR):
            os.makedirs(REPORT_DIR)

        SQLITE_DB_PATH = os.path.join(REPORT_DIR, "data.db")
    else:
        SQLITE_DB_PATH = ":memory:"

    main(SQLITE_DB_PATH)
    logging.info("Finished AWS/Qualys Sync")
