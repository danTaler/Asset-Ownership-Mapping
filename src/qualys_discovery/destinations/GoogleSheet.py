import time
import os
import logging

import gspread


class GoogleSheet:
    def __init__(self, reports, config=None):
        self._reports = reports
        self._config = config or {}

        # Load unset access config from the env
        self._config["access"] = {
            k.replace("GOOGLE_API_", "").lower(): v
            for k, v in os.environ.items()
            if k.startswith("GOOGLE_API_")
        } | self._config.get("access", {})

        self._gsheet = self._open_sheet(self._config["access"])

    def sync(self):
        for sheet_name, report_config in self._config["reports"].items():
            report_id = report_config["id"]
            logging.info(
                'Running Report: sheet_name="%s" report_id="%s"',
                sheet_name,
                report_id,
            )
            report = getattr(self._reports, report_config["id"])()
            sheet = self._gsheet.worksheet(sheet_name)
            self._reset_all_worksheets(sheet)
            self._update_sheet(sheet, report)

    @staticmethod
    def _open_sheet(google_auth):
        """
        Authenticating to Google API and open the sheet
        """
        gc = gspread.service_account_from_dict(
            {
                "type": "service_account",
                "project_id": google_auth["project_id"],
                "private_key_id": google_auth["private_key_id"],
                "private_key": google_auth["private_key"].replace(
                    "\\n", "\n"
                ),  # remove double backward slashes  \\n
                "client_email": google_auth["client_email"],
                "client_id": google_auth["client_id"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": google_auth["client_x509_cert_url"],
            }
        )

        return gc.open_by_url(google_auth["sheet_url"])

    def _reset_all_worksheets(self, sheet):
        """
        Reset the spreadsheet
        """
        sheet.batch_clear([self._config["reports"][sheet.title]["header"]])
        sheet.format(
            self._config["reports"][sheet.title]["header"],
            {
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                "textFormat": {"bold": True},
            },
        )

        sheet.batch_clear([self._config["reports"][sheet.title]["rows"]])
        sheet.format(
            self._config["reports"][sheet.title]["rows"],
            {
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
            },
        )

    def _update_cells(self, sheet, cell_range, cell_values):
        """
        A helper to apply cell value updates to a cell range.

        * Cell range must be equal to or larger than cell values
        * Done in a batch to avoid hammering the API too hard.
        """
        cell_list = sheet.range(cell_range)
        buf = []

        for i, value in enumerate(cell_values):
            cell_list[i].value = value
            buf.append(cell_list[i])

            # Reduce the size of the updates to smaller sets
            if len(buf) >= 1000:
                self._apply_cell_updates(sheet, buf)
                buf.clear()

        # Handle any remaining cells
        if buf:
            self._apply_cell_updates(sheet, buf)

    def _apply_cell_updates(self, sheet, cells, count=0):
        delay = self._config.get("api", {}).get("delay", 5)

        try:
            # Don't go over rate limit
            time.sleep(delay)
            sheet.update_cells(cells)
        except Exception:
            if count:
                logging.error("Could Not Update Cells")
            else:
                logging.error("Could Not Update Cells: Sleeping and trying again")
                # Wait out the remainder of the wait limit time if we do
                time.sleep(60 - delay)
                self._apply_cell_updates(sheet, cells, count + 1)

    def _update_sheet(self, sheet, report):
        """
        Set all rows at one API call.
        """
        logging.info("Report Stats: length=%d", len(report))
        self._update_cells(
            sheet,
            self._config["reports"][sheet.title]["header"],
            report[0],
        )
        self._update_cells(
            sheet,
            self._config["reports"][sheet.title]["rows"],
            [v for row in report[1:] for v in row],
        )
