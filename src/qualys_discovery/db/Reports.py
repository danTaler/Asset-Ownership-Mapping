class Reports:
    """
    For generating reports on the different tables

    The report method should match a given report "id", that is in the config
    that references a report id, that string should be the method that's called
    to generate the report.
    """

    def __init__(self, cur, con):
        self._cur = cur
        self._con = con

    def aws_accounts_report(self):
        """
        List AWS Accounts:
        """
        self._cur.execute(
            """
            SELECT
                aws_accounts.account_id,
                aws_accounts.account_name,
                aws_accounts.account_email,
                aws_accounts.account_status,
                aws_accounts.account_metadata_bu,
                aws_accounts.account_metadata_customer_name,
                aws_accounts.account_metadata_primary_contact,
                aws_accounts.account_metadata_contact_email
            FROM
                aws_accounts
            ORDER BY
                aws_accounts.account_id DESC;
            """
        )

        return [
            (
                "AccountId",
                "AccountName",
                "AccountEmail",
                "AccountStatus",
                "AccountBU",
                "CustomerName",
                "PrimaryContact",
                "ContactEmail",
            )
        ] + self._cur.fetchall()

    def aws_inventory_report(self):
        """
        List Qualys assets with AWS details from DB:
        """
        self._cur.execute(
            """
            SELECT
                qualys_assets.asset_id,
                qualys_assets.asset_name,
                qualys_assets.agent_status,
                qualys_assets.last_checked_in,
                aws_accounts.account_id,
                aws_accounts.account_name,
                aws_accounts.account_email,
                aws_accounts.account_metadata_bu,
                aws_accounts.account_metadata_customer_name,
                aws_accounts.account_metadata_primary_contact,
                aws_accounts.account_metadata_contact_email,
                aws_entries.region,
                aws_entries.region_ec2_count,
                aws_entries.instance_id,
                aws_entries.instance_type,
                aws_entries.instance_public_ip,
                aws_entries.instance_public_dns_name,
                aws_entries.instance_private_ip,
                aws_entries.instance_state,
                aws_entries.instance_launch_date,
                aws_entries.instance_platform_details,
                aws_entries.app_code,
                aws_entries.service_owner,
                aws_entries.tags_names
            FROM
                aws_entries
            LEFT JOIN
                qualys_assets
            ON
                qualys_assets.aws_instance_id = aws_entries.instance_id
            JOIN
                aws_accounts
            ON
                aws_entries.account_id = aws_accounts.account_id
            ORDER BY
                aws_accounts.account_id;
            """
        )

        return [
            (
                "QualysAssetId",
                "QualysAssetName",
                "AgentStatus",
                "LastCheckedIn",
                "AccountId",
                "AccountName",
                "AccountEmail",
                "AccountBU",
                "CustomerName",
                "PrimaryContact",
                "ContactEmail",
                "Region",
                "RegionEC2Count",
                "InstanceId",
                "InstanceType",
                "PublicIP",
                "DNS",
                "PrivateIP",
                "InstanceState",
                "InstanceLaunchDate",
                "InstanceOS",
                "AppCode",
                "ServiceOwner",
                "Tags",
            )
        ] + self._cur.fetchall()

    def openstack_inventory_report(self):
        """
        List OpenStacks with Qualys
        """
        self._cur.execute(
            """
            SELECT
                qualys_assets.qweb_host_id,
                qualys_assets.fqdn,
                qualys_assets.ip_address,
                qualys_assets.agent_status,
                qualys_assets.last_checked_in,
                openstack_servers.project_name,
                openstack_servers.project_id,
                openstack_servers.env,
                openstack_servers.server_name,
                openstack_servers.server_id,
                openstack_servers.status,
                openstack_servers.created,
                openstack_servers.ip_address_0,
                openstack_servers.ip_address_1,
                openstack_servers.ip_address_access,
                openstack_servers.metadata_hostname,
                openstack_servers.metadata_owner,
                openstack_servers.metadata_appcode
            FROM
                openstack_servers
            LEFT JOIN
                qualys_assets
            ON
                openstack_servers.ip_address_0 = qualys_assets.ip_address
            OR
                openstack_servers.ip_address_1 = qualys_assets.ip_address
            ORDER BY
                openstack_servers.project_name
            """
        )

        return [
            (
                "QualysID",
                "FQDN",
                "QualysIP",
                "AgentStatus",
                "LastCheckedIn",
                "ProjectName",
                "ProjectID",
                "ENV",
                "ServerName",
                "ServerId",
                "Status",
                "Created",
                "IPAddress-1",
                "IPAddress-2",
                "IPAccess",
                "Hostname",
                "Owner",
                "AppCode",
            )
        ] + self._cur.fetchall()
