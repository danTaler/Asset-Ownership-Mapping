import os
import logging
import sqlite3

from db.NmapDB import NmapDB
from sources.NmapScans import NmapScans

REPORT_DIR = os.environ.get("REPORT_DIR")
DATACENTERS = [
    {
        "name": "xxxxxx.xxxxxx",
        "ip_range": "x.x.x.x",
    },
]

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
)


def main(db_path):
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()

        # -- Nmap Scans ---
        logging.info("Starting Nmap Scans")
        NmapScans(NmapDB(cur, con), datacenters=DATACENTERS).sync()
        logging.info("Finished Nmap Scans")


if __name__ == "__main__":
    logging.info("Starting Nmap Scans Sync")

    if REPORT_DIR:
        if not os.path.exists(REPORT_DIR):
            os.makedirs(REPORT_DIR)

        SQLITE_DB_PATH = os.path.join(REPORT_DIR, "data-nmap.db")
    else:
        SQLITE_DB_PATH = ":memory:"

    main(SQLITE_DB_PATH)
    logging.info("Finished Nmap Scans Sync")
