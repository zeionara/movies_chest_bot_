# -*- coding: utf-8 -*-

import paramiko
from paramiko import SSHClient
from scp import SCPClient

from constants import scp_host, scp_port, scp_username, scp_password

def send_file(local_file_name, remote_file_name):

    ssh = SSHClient()

    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(scp_host, port=scp_port, username=scp_username, password=scp_password)

    scp = SCPClient(ssh.get_transport())

    scp.put(local_file_name, remote_file_name)

def read_file(remote_file_name):

    ssh = SSHClient()

    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(scp_host, port=scp_port, username=scp_username, password=scp_password)

    scp = SCPClient(ssh.get_transport())
    try:
        print('getting result : ',scp.get(remote_file_name))
    except scp.SCPException:
        return False
    else:
        return True
