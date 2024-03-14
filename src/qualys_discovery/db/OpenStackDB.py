class OpenStackDB:
    def __init__(self, cur, con):
        self._cur = cur
        self._con = con

    def reset(self):
        self._cur.execute("DROP TABLE IF EXISTS openstack_projects")
        self._cur.execute("DROP TABLE IF EXISTS openstack_servers")
        self._cur.execute(
            """
            CREATE TABLE openstack_projects (
                project_id INTEGER,
                project_name text,
                project_description text,
                project_tags text,
                project_enabled text
            )
            """
        )
        # table servers:
        self._cur.execute(
            """
            CREATE TABLE openstack_servers (
                project_id text,
                project_name text,
                env text,
                server_id INTEGER,
                server_name text,
                status text,
                created text,
                ip_address_0 text,
                ip_address_1 text,
                ip_address_access text,
                metadata_hostname text,
                metadata_owner text,
                metadata_appcode text
            )
            """
        )

    def insert_project(self, project):
        """
        Insert Into OpenStack projects
        """
        self._cur.execute(
            """
            INSERT INTO openstack_projects (
                project_id,
                project_name,
                project_description,
                project_tags,
                project_enabled
            ) VALUES (?,?,?,?,?)
            """,
            (
                project.id,
                project.name,
                project.description,
                project.tags,
                project.enabled,
            ),
        )

        self._con.commit()

    def insert_server(self, server):
        """
        Insert Into OpenStack servers
        """
        self._cur.execute(
            """
            INSERT INTO openstack_servers (
                project_id,
                project_name,
                env,
                server_id,
                server_name,
                status,
                created,
                ip_address_0,
                ip_address_1,
                ip_address_access,
                metadata_hostname,
                metadata_owner,
                metadata_appcode
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                server.project.id,
                server.project.name,
                server.env,
                server.id,
                server.name,
                server.status,
                server.created,
                server.ip_address_0,
                server.ip_address_1,
                server.ip_address_access,
                server.metadata_hostname,
                server.metadata_owner,
                server.metadata_appcode,
            ),
        )

        self._con.commit()
