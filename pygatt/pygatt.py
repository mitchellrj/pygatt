from __future__ import print_function

# from collections import defaultdict
from binascii import unhexlify
import logging
import logging.handlers
# import string
import time

from bluegiga.bgble import BLED112Backend
from constants import(
    BACKEND, DEFAULT_CONNECT_TIMEOUT_S, LOG_LEVEL, LOG_FORMAT
)


class BluetoothLEDevice(object):
    """
    Interface for a Bluetooth Low Energy device that can use either the Bluegiga
    BLED112 (cross platform) or GATTTOOL (Linux only) as the backend.
    """
    def __init__(self, mac_address, backend, logfile=None):
        """
        Initialize.

        mac_address -- a string containing the mac address of the BLE device in
                       the following format: "XX:XX:XX:XX:XX:XX"
        backend -- backend to use. One of pygatt.constants.backend.
        logfile -- the file in which to write the logs.
        """
        # Set up logging FIXME clean up
        logging.basicConfig(filename='example.log')  # FIXME remove
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(LOG_LEVEL)

        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(LOG_LEVEL)
        self._formatter = logging.Formatter(LOG_FORMAT)
        self._console_handler.setFormatter(self._formatter)
        self._logger.addHandler(self._console_handler)

        # Select backend, store mac address
        if backend == BACKEND['BLED112']:
            self._backend = BLED112Backend('COM7')  # FIXME port name
            self._mac_address = bytearray(
                [int(b, 16) for b in mac_address.split(":")])
        elif backend == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise ValueError("backend", backend)
        self._backend_type = backend

    def bond(self):
        """
        Securely Bonds to the BLE device.
        """
        if self._backend_type == BACKEND['BLED112']:
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def connect(self, timeout=DEFAULT_CONNECT_TIMEOUT_S):
        """
        Connect to the BLE device.

        timeout -- the length of time to try to establish a connection before
                   returning.

        Returns True if the connection was made successfully.
        Returns False otherwise.
        """
        if self._backend_type == BACKEND['BLED112']:
            return self._backend.connect(self._mac_address, timeout=timeout)
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def char_read(self, uuid):
        """
        Reads a Characteristic by UUID.

        uuid -- UUID of Characteristic to read as a string.

        Returns a bytearray containing the characteristic value on success.
        Returns None on failure.
        """
        if self._backend_type == BACKEND['BLED112']:
            handle = self._get_handle(uuid)
            if handle is None:
                return None
            return self._backend.char_read(handle)
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def char_write(self, uuid, value, wait_for_response=False):
        """
        Writes a value to a given characteristic handle.

        uuid --
        value --
        wait_for_response --
        """
        if self._backend_type == BACKEND['BLED112']:
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def exit(self):
        """
        Cleans up. Run this when done using the BluetoothLEDevice object.
        """
        if self._backend_type == BACKEND['BLED112']:
            self._backend.disconnect()
            self._backend.stop()
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def get_rssi(self):
        """
        Get the receiver signal strength indicator (RSSI) value from the BLE
        device.

        Returns the RSSI value on success.
        Returns None on failure.
        """
        if self._backend_type == BACKEND['BLED112']:
            # The BLED112 has some strange behavior where it will return 25 for
            # the RSSI value sometimes... Try a maximum of 3 times.
            for i in range(0, 3):
                rssi = self._backend.get_rssi()
                if rssi != 25:
                    return rssi
                time.sleep(0.1)
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def run(self):
        """Run a background thread to listen for notifications.
        """
        if self._backend_type == BACKEND['BLED112']:
            # Nothing to do
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def stop(self):
        """Stop the backgroud notification handler in preparation for a
        disconnect.
        """
        if self._backend_type == BACKEND['BLED112']:
            # Nothing to do
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def subscribe(self, uuid, callback=None, indication=False):
        """
        Enables subscription to a Characteristic with ability to call callback.

        uuid --
        callback --
        indication --
        """
        if self._backend_type == BACKEND['BLED112']:
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def _get_handle(self, uuid):
        """
        Get the handle associated with the UUID.

        uuid -- a UUID in string format.
        """
        uuid = self._uuid_bytearray(uuid)
        if self._backend_type == BACKEND['BLED112']:
            return self._backend.get_handle(uuid)
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def _uuid_bytearray(self, uuid):
        """
        Turns a UUID string in the format "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        to a bytearray.

        uuid -- the UUID to convert.

        Returns a bytearray containing the UUID.
        """
        return unhexlify(uuid.replace("-", ""))

# FIXME going to use these?
    def _expect(self, expected):  # timeout=pygatt.constants.DEFAULT_TIMEOUT_S):
        """We may (and often do) get an indication/notification before a
        write completes, and so it can be lost if we "expect()"'d something
        that came after it in the output, e.g.:

        > char-write-req 0x1 0x2
        Notification handle: xxx
        Write completed successfully.
        >

        Anytime we expect something we have to expect noti/indication first for
        a short time.
        """
        if self._backend_type == BACKEND['BLED112']:
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)

    def _handle_notification(self, msg):
        """
        Receive a notification from the connected device and propagate the value
        to all registered callbacks.
        """
        if self._backend_type == BACKEND['BLED112']:
            pass
        elif self._backend_type == BACKEND['GATTTOOL']:
            raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("backend", self._backend_type)
