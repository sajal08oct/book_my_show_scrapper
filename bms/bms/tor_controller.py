import logging
import sys
import socket
import time
import requests
import stem
import stem.control

import urllib.request

# Tor settings
TOR_ADDRESS = "127.0.0.1"       # The Docker-Compose service in which this code is running should be linked to the "tor" service.
TOR_CONTROL_PORT = 9051         # This is configured in /etc/tor/torrc by the line "ControlPort 9051" (or by launching Tor with "tor -controlport 9051")
TOR_PASSWORD = "yt@123$"            # The Tor password is written in the docker-compose.yml file. (It is passed as a build argument to the 'tor' service).

# Privoxy settings
PRIVOXY_ADDRESS = "127.0.0.1"     # This assumes this code is running in a Docker-Compose service linked to the "privoxy" service
PRIVOXY_PORT = 8118             # This is determined by the "listen-address" in Privoxy's "config" file
HTTP_PROXY = 'http://{address}:{port}'.format(address=PRIVOXY_ADDRESS, port=PRIVOXY_PORT)
headers=hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
logger = logging.getLogger(__name__)


class TorController(object):
    def __init__(self):
        self.controller = stem.control.Controller.from_port(port=TOR_CONTROL_PORT)
        self.controller.authenticate(password=TOR_PASSWORD)

    def request_ip_change(self):
        self.controller.signal(stem.Signal.NEWNYM)

    def get_ip(self):
        '''Check what the current IP address is (as seen by IPEcho).'''

        def _set_urlproxy():
            proxy_support = urllib.request.ProxyHandler({"http": "http://127.0.0.1:8118"})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)

            # request a URL
            # via the proxy

        _set_urlproxy()
        request = urllib.request.Request(url="http://icanhazip.com/", headers=headers)
        return urllib.request.urlopen(request).read()

    def change_ip(self):
        '''Signal a change of IP address and wait for confirmation from IPEcho.net'''
        current_ip = self.get_ip()
        logger.debug("Initializing change of identity from the current IP address, {current_ip}".format(current_ip=current_ip))
        self.request_ip_change()
        while True:
            new_ip = self.get_ip()
            if new_ip == current_ip:
                logger.debug("The IP address is still the same. Waiting for 1 second before checking again...")
                time.sleep(1)
            else:
                break
        logger.debug("The IP address has been changed from {old_ip} to {new_ip}".format(old_ip=current_ip, new_ip=new_ip))
        return new_ip

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.controller.close()


def change_identity():
    with TorController() as tor_controller:
        tor_controller.change_ip()

with TorController() as tor_controller:
    tor_controller.change_ip()