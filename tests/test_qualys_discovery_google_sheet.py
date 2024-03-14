import os

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from qualys_discovery.destinations.GoogleSheet import GoogleSheet


class MockSheet:
    """
    Stub out multiple components of the gspread api for testing
    """

    def __init__(self):
        self.urls = []
        self.worksheets = {}
        self.title = None

    def open_by_url(self, url):
        """
        Store the URL used to open it
        """
        self.urls.append(url)
        return self

    def worksheet(self, title):
        """
        Store info about the calls
        """
        self.worksheets[title] = {
            "batch_clear": [],
            "format": [],
            "range": [],
            "update_cells": [],
        }
        self.title = title
        return self

    def batch_clear(self, clear_ranges):
        self.worksheets[self.title]["batch_clear"].append(clear_ranges)

    def format(self, fmt_range, opts):
        self.worksheets[self.title]["format"].append((fmt_range, opts))

    def range(self, sel_range):
        self.worksheets[self.title]["range"].append(sel_range)
        # Generate a bunch of "cell" objects (more than the tests need)
        return [type("cell", tuple(), {}) for _ in range(500)]

    def update_cells(self, cells):
        self.worksheets[self.title]["update_cells"].append(cells)


class GoogleSheetTest(TestCase):
    def setUp(self):
        # It should be able to be set up
        os.environ.update(
            {
                "GOOGLE_API_SERVICE_ACCOUNT": "foo",
                "GOOGLE_API_PROJECT_ID": "1",
                "GOOGLE_API_PRIVATE_KEY_ID": "2",
                "GOOGLE_API_PRIVATE_KEY": "<some key>",
                "GOOGLE_API_CLIENT_EMAIL": "no-reply@xxxxx.com",
                "GOOGLE_API_CLIENT_ID": "3",
                "GOOGLE_API_CLIENT_x509_CERT_URL": "https://some-url",
                "GOOGLE_API_SHEET_URL": "https://google.com/some/sheet",
            }
        )

    @patch("gspread.service_account_from_dict")
    def test_init(self, mock_gspread_service_account_from_dict):
        # It should set the config based on the env
        GoogleSheet(MagicMock())
        opts = mock_gspread_service_account_from_dict.call_args[0][0]
        self.assertDictEqual(
            opts,
            {
                "type": "service_account",
                "project_id": "1",
                "private_key_id": "2",
                "private_key": "<some key>",
                "client_email": "xxxxxx",
                "client_id": "3",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://some-url",
            },
        )

        # IT should also support options passed in to the constructor
        GoogleSheet(MagicMock(), config={"access": {"project_id": "foo"}})
        opts = mock_gspread_service_account_from_dict.call_args[0][0]
        self.assertDictEqual(
            opts,
            {
                "type": "service_account",
                "project_id": "foo",
                "private_key_id": "2",
                "private_key": "<some key>",
                "client_email": "xxxxxx",
                "client_id": "3",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://some-url",
            },
        )

    @patch("gspread.service_account_from_dict")
    def test_sync(self, mock_gspread_service_account_from_dict):
        # Set up mocks
        mock_sheet = MockSheet()
        mock_gspread_service_account_from_dict.return_value = mock_sheet
        mock_reports = MagicMock()
        mock_reports.aws_accounts_report.return_value = [
            ("Header 1", "Header 2", "Header 3"),
            ("Account Value 1", "Account Value 2", "Account Value 3"),
            ("Account Value 1", "Account Value 2", "Account Value 3"),
        ]
        mock_reports.aws_inventory_report.return_value = [
            ("Header 1", "Header 2", "Header 3"),
            ("Inventory Value 1", "Inventory Value 2", "Inventory Value 3"),
            ("Inventory Value 1", "Inventory Value 2", "Inventory Value 3"),
        ]

        GoogleSheet(
            mock_reports,
            config={
                "api": {
                    "delay": 0,
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
            },
        ).sync()

        accounts = mock_sheet.worksheets["Accounts"]
        inventory = mock_sheet.worksheets["Inventory"]
        updated_account_cells = accounts.pop("update_cells")
        updated_inventory_cells = inventory.pop("update_cells")

        # Check Accounts header row
        self.assertEqual(len(updated_account_cells[0]), 3)
        self.assertEqual(updated_account_cells[0][1].value, "Header 2")

        # Check Accounts body
        self.assertEqual(len(updated_account_cells[1]), 6)
        self.assertEqual(updated_account_cells[1][1].value, "Account Value 2")

        # Check Inventory header row
        self.assertEqual(len(updated_inventory_cells[0]), 3)
        self.assertEqual(updated_inventory_cells[0][1].value, "Header 2")

        # Check Inventory body
        self.assertEqual(len(updated_inventory_cells[1]), 6)
        self.assertEqual(updated_inventory_cells[1][1].value, "Inventory Value 2")

        # Confirm the operations on the sheets are what we expect
        self.assertDictEqual(
            accounts,
            {
                "batch_clear": [["A1:H1"], ["A2:H9999"]],
                "format": [
                    (
                        "A1:H1",
                        {
                            "textFormat": {"bold": True},
                            "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                        },
                    ),
                    (
                        "A2:H9999",
                        {
                            "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                        },
                    ),
                ],
                "range": ["A1:H1", "A2:H9999"],
            },
        )

        self.assertDictEqual(
            inventory,
            {
                "batch_clear": [["A1:X1"], ["A2:X9999"]],
                "format": [
                    (
                        "A1:X1",
                        {
                            "textFormat": {"bold": True},
                            "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                        },
                    ),
                    (
                        "A2:X9999",
                        {
                            "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                        },
                    ),
                ],
                "range": ["A1:X1", "A2:X9999"],
            },
        )
