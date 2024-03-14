from unittest import TestCase
from datetime import datetime

from qualys_uninstall_purge_inactive_agents import (
    main_uninstall_inactive_agents_PSSC_4days as script,
)


class QualysUninstallPurgeInactiveAgentsTest(TestCase):
    def test_get_date(self):
        """
        Just confirm the date's being formatted correctly
        """
        date = datetime.strptime(script.get_date(), "%Y-%m-%d")
        older_date = datetime.strptime(script.get_date(days_ago=4), "%Y-%m-%d")
        self.assertEqual((date - older_date).days, 4)
