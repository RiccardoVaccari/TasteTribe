from sshtunnel import SSHTunnelForwarder

server = SSHTunnelForwarder(
    ssh_address_or_host="129.152.27.5",
    ssh_username="ubuntu",
    ssh_pkey="DB-PKEY",
    remote_bind_address=("localhost", 5432),
)

server.start()
