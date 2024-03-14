class QualysDB:
    def __init__(self, cur, con):
        self._cur = cur
        self._con = con

    def reset(self):
        """
        Creating DB table for Qualys entries.
        """
        self._cur.execute("DROP TABLE IF EXISTS qualys_assets")
        self._cur.execute(
            """
            CREATE TABLE qualys_assets (
                asset_id INTEGER,
                asset_name text,
                agent_status text,
                aws_instance_id text,
                fqdn text,
                ip_address text,
                last_checked_in text,
                os text,
                qweb_host_id INTEGER
            )
            """
        )

    def insert_asset(self, asset):
        """
        Inserting Qualys entries into DB table
        """
        self._cur.execute(
            """
            INSERT INTO qualys_assets (
                asset_id,
                asset_name,
                agent_status,
                aws_instance_id,
                fqdn,
                ip_address,
                last_checked_in,
                os,
                qweb_host_id
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                asset.id,
                asset.name,
                asset.agent_status,
                asset.aws_instance_id,
                asset.fqdn,
                asset.ip_address,
                asset.last_checked_in,
                asset.os,
                asset.qweb_host_id,
            ),
        )

        self._con.commit()
