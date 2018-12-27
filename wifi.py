"""
network functionality

@author Russ Winch
@version 1.1
"""

import json
import network
import time


class Wifi(object):
    def __init__(self):
        self.net = network.WLAN(network.STA_IF)

    def _retrieve_credentials(self, filename='credentials.json'):
        """
        Collects wifi uid and password from json file containing
        `uid` and `passw` keys
        """
        with open(filename) as c:
            creds = json.loads(c.read())
            return creds['uid'], creds['passw']

    def connect(self):
        timeout = 15  # seconds

        if not self.net.isconnected():
            try:
                uid, passw = self._retrieve_credentials()
            except OSError:
                print("Failed due to missing wifi credentials file")
                return False
            except (KeyError, ValueError):
                print("Failed due to incorrectly formatted wifi credentials file")
                return False

            print("connecting to network: {}".format(uid))
            self.net.active(True)
            self.net.connect(uid, passw)

            print("timeout in {} seconds".format(timeout))
            timeout_time = time.time() + timeout
            while not self.net.isconnected() and time.time() < timeout_time:
                if timeout != timeout_time - time.time():
                    timeout = timeout_time - time.time()
                    print("Timeout in {} seconds".format(timeout))

            if self.net.isconnected():
                print("Connected! IP config: {}".format(self.net.ifconfig()))
            else:
                print("Couldn't connect. Timed out!")
        return self.net.isconnected()

    def test_connected(self):
        print(self.net.status())
        print(self.net.ifconfig())
        return self.net.isconnected()
