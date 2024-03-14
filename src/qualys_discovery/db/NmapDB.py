class NmapDB:
    def __init__(self, cur, con):
        self._cur = cur
        self._con = con

    def reset(self):
        self._cur.execute("DROP TABLE IF EXISTS nmap_results")
        self._cur.execute(
            """
            CREATE TABLE nmap_results (
                datacenter text,
                public_ip text,
                ports text,
                hostname text
            )
            """
        )

    def insert_nmap_results(self, nmap_results):
        """
        Insert Into nmap_results
        """
        self._cur.execute(
            """
            INSERT INTO nmap_results (
                datacenter,
                public_ip,
                ports,
                hostname
            ) VALUES (?,?,?,?)
            """,
            (
                nmap_results.datacenter,
                nmap_results.public_ip,
                ",".join(map(str, nmap_results.ports)),
                nmap_results.hostname,
            ),
        )

        self._con.commit()
