#!/usr/bin/env python3

import argparse
import logging
import os
import os.path
import shutil
import subprocess
import sys
import tempfile
import time

# third-party modules
import openstack


LOG = logging.getLogger(__name__)
POLL_DELAY = 5  # seconds


def setup_logging(level=logging.INFO):
    logging.basicConfig(stream=sys.stderr, level=level)


def setup_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', required=True, metavar='NAME',
                        dest='cloud_name',
                        help='Cloud name defined in clouds.yaml')
    parser.add_argument('--hostsdir', metavar='DIR',
                        help='Hosts directory')
    parser.add_argument('--loglevel', metavar='LEVEL', default='INFO',
                        choices=['DEBUG', 'ERROR', 'WARNING', 'INFO',
                                 'CRITICAL'])
    parser.add_argument('--use-sudo', action='store_true',
                        help='Use sudo when running dnsmasq')
    parser.add_argument('--domain', default='zosci')
    return parser.parse_args()


def list_servers(conn):
    print("List Servers:")

    for server in conn.compute.servers():
        yield server


def get_connection(cloud_name):
    return openstack.connection.from_config(cloud=cloud_name)


def run_dnsmasq(hostsdir, use_sudo=False):
    if use_sudo:
        cmd = ['sudo']
    else:
        cmd = []

    with open('/etc/dnsmasq.d/dns-service', 'w') as f:
        f.write(f'hostsdir={hostsdir}\n')
        f.write(f'addn-hosts={hostsdir}/hosts\n')
    # cmd += ['dnsmasq',
    #         f'--hostsdir={hostsdir}',
    #         f'--pid-file={pidfile}']
    cmd += ['systemctl', 'restart', 'dnsmasq']
    return subprocess.check_output(cmd)


def stop_dnsmasq(hostsdir=None, use_sudo=False):
    if use_sudo:
        cmd = ['sudo']
    else:
        cmd = []
    cmd += ['systemctl', 'stop', 'dnsmasq']
    return subprocess.check_output(cmd)


def main():
    opts = setup_opts()
    setup_logging(getattr(logging, opts.loglevel))
    conn = get_connection(opts.cloud_name)

    if opts.hostsdir:
        hostsdir = opts.hostsdir
        created_hostsdir = False
    else:
        hostsdir = tempfile.mkdtemp(suffix='.dns-service')
        os.chmod(hostsdir, 0o755)
        created_hostsdir = True

    try:
        pidfile = None
        output = run_dnsmasq(hostsdir, use_sudo=opts.use_sudo)
        LOG.debug(str(output))
        while True:
            hosts_fpath = os.path.join(hostsdir, 'hosts')
            if not os.path.isfile(hosts_fpath):
                with open(hosts_fpath, 'w') as f:
                    pass
            os.chmod(hosts_fpath, 0o644)
            with open(hosts_fpath, 'w') as hostsfile:
                for server in list_servers(conn):
                    LOG.info('Server found: %s', str(server))
                    print(dir(server))
                    hostname = server['name']
                    for net_name, addresses in server.get('addresses',
                                                          {}).items():
                        for addr in addresses:
                            ip_addr = addr['addr']
                            entry = f'{ip_addr} {hostname}.{opts.domain}\n'
                            LOG.info('Adding: %s', entry)
                            hostsfile.write(entry)

            time.sleep(POLL_DELAY)
    except KeyboardInterrupt:
        LOG.info('Ctrl-C: exiting ...')
    finally:
        if pidfile:
            stop_dnsmasq()
        if created_hostsdir:
            shutil.rmtree(hostsdir)


if __name__ == "__main__":
    main()
