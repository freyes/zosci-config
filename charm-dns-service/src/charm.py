#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import logging
import os
import pprint
import subprocess

import jinja2
import ops

logger = logging.getLogger(__name__)
__this__ = os.path.abspath(__file__)
DNS_SERVICE_SCRIPT = os.path.join(os.path.dirname(__this__),
                                  'dns-service.py')
assert os.path.isfile(DNS_SERVICE_SCRIPT), f'No such file {DNS_SERVICE_SCRIPT}'

ETC_OPENSTACK = '/etc/openstack'
CLOUDS_YAML_PATH = '/etc/openstack/clouds.yaml'
CLOUDS_YAML_TPL = """
clouds:
  {{ name }}:
    auth:
      username: {{ credential.attribute.username }}
      password: {{ credential.attribute.password }}
      project_name: {{ credential.attribute.tenant-name }}
      project_domain_name: {{ credential.attribute.project-domain-name }}
      user_domain_name: {{ credential.attribute.user-domain-name }}
      auth_url: {{ endpoint }}
    inteface: {{ interface|default('public') }}
    region_name: {{ region }}
"""
DNS_SERVICE_UNIT="""
[Unit]
Description=DNS Service
After=network.target

[Service]
Environment=PYTHONPATH={{ charmdir }}/venv
ExecStart=/usr/bin/python3 {{ charmdir }}/src/dns-service.py --cloud {{ name }} --loglevel {{ loglevel }}
Type=simple
Restart=always

[Install]
WantedBy=default.target
RequiredBy=network.target
"""

class CloudCredentialsAccessDenied(Exception):
    pass


class CharmDnsServiceCharm(ops.CharmBase):
    """Charm the application."""

    _stored = ops.framework.StoredState()

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self._stored.set_default(current_mode="test")
        self._stored.set_default(creds={})

        framework.observe(self.on.start, self._on_start)
        #framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        try:
            self._update_credentials()
        except CloudCredentialsAccessDenied:
            self.unit.status = ops.BlockedStatus(
                'Cannot access to the cloud credentials, use juju trust'
            )
            return
        self._render_clouds_yaml()
        creds = self._load_creds()
        cmd = [DNS_SERVICE_SCRIPT, '--cloud', creds['name']]
        if self.config['debug']:
            cmd += ['--loglevel', 'DEBUG']
        subprocess.run(cmd)
        self.unit.status = ops.ActiveStatus()

    def _update_credentials(self):
        logger.info('Acessing to cloud credentials')
        required_fields = [
            "auth_url",
            "region",
            "username",
            "password",
            "user_domain_name",
            "project_domain_name",
            "project_name",
        ]
        # pre-populate with empty values to avoid key and arg errors
        creds_data = {field: "" for field in required_fields}

        try:
            # try to use Juju's trust feature
            logger.info("Checking credentials-get for credentials")
            result = subprocess.run(
                ["credential-get", '--format=json'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            creds_data = json.loads(result.stdout.decode("utf8"))
            logger.info('Credentials found.')
            logger.debug('Credentials: %s', pprint.pformat(creds_data))
            self._save_creds(creds_data)
        except subprocess.CalledProcessError as e:
            if "permission denied" not in e.stderr.decode("utf8"):
                logger.error(str(e))
                raise CloudCredentialsAccessDenied()

    def _load_creds(self):
        return json.loads(self._stored.creds)

    def _save_creds(self, creds_data):
        self._stored.creds = json.dump(creds_data)

    def _render_clouds_yaml(self):
        logger.info('Rendering clouds.yaml')
        env = jinja2.Environment(loader=jinja2.BaseLoader)
        rtemplate = env.from_string(CLOUDS_YAML_TPL)
        data = rtemplate.render(**self._load_creds())

        basedir = os.path.basedir(CLOUDS_YAML_PATH)
        if not os.path.isdir(basedir):
            os.mkdir(basedir, mode=0o755)

        with open(CLOUDS_YAML_PATH, 'w') as f:
            f.write(data)
            f.flush()


if __name__ == "__main__":  # pragma: nocover
    ops.main(CharmDnsServiceCharm)  # type: ignore
