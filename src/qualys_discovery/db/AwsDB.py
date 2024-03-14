class AwsDB:
    def __init__(self, cur, con):
        self._cur = cur
        self._con = con

    def reset(self):
        self._cur.execute("DROP TABLE IF EXISTS aws_accounts")
        self._cur.execute("DROP TABLE IF EXISTS aws_entries")
        self._cur.execute(
            """
                    CREATE TABLE aws_accounts(
                        account_id INTEGER,
                        account_name text,
                        account_email text,
                        account_status text,
                        account_metadata_bu text,
                        account_metadata_customer_name text,
                        account_metadata_primary_contact text,
                        account_metadata_contact_email text
                    )
                """
        )
        self._cur.execute(
            """
                    CREATE TABLE aws_entries(
                        account_id INTEGER,
                        region text,
                        region_ec2_count text,
                        instance_id text,
                        instance_type text,
                        instance_public_ip text,
                        instance_public_dns_name text,
                        instance_private_ip text,
                        instance_state text,
                        instance_launch_date text,
                        instance_platform_details text,
                        app_code text,
                        service_owner text,
                        tags_names text
                    )
                """
        )

    def insert_aws_account(self, account):
        """
        Insert Into AWS Accounts
        """
        self._cur.execute(
            """
            INSERT INTO aws_accounts (
                account_id,
                account_name,
                account_email,
                account_status,
                account_metadata_bu,
                account_metadata_customer_name,
                account_metadata_primary_contact,
                account_metadata_contact_email
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                account.id,
                account.name,
                account.email,
                account.status,
                account.metadata_bu,
                account.metadata_customer_name,
                account.metadata_primary_contact,
                account.metadata_contact_email,
            ),
        )

        self._con.commit()

    def insert_aws_entry(self, entry):
        """
        Inserting AWS entries to DB table
        """
        self._cur.execute(
            """
                INSERT INTO aws_entries (
                    account_id,
                    region,
                    region_ec2_count,
                    instance_id,
                    instance_type,
                    instance_public_ip,
                    instance_public_dns_name,
                    instance_private_ip,
                    instance_state,
                    instance_launch_date,
                    instance_platform_details,
                    app_code,
                    service_owner,
                    tags_names

                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
            (
                entry.account_id,
                entry.region,
                entry.region_ec2_count,
                entry.instance_id,
                entry.instance_type,
                entry.instance_public_ip,
                entry.instance_public_dns_name,
                entry.instance_private_ip,
                entry.instance_state,
                entry.instance_launch_date,
                entry.instance_platform_details,
                entry.app_code,
                entry.service_owner,
                entry.tags_names,
            ),
        )

        self._con.commit()
