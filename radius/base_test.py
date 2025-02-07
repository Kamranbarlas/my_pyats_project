# auth_tests/base_test.py

from pyats.aetest import Testcase, test, setup, cleanup
from pyats.topology import loader

class AuthTestBase(Testcase):
    """
    Base test class providing shared functionality to connect to
    the device, execute commands, and store references.
    """
    import pdb; pdb.set_trace()
    @setup
    def connect_to_device(self, testbed):
        """
        Setup step: Connect to the device using pyATS testbed
        """
        self.testbed = loader.load(testbed)
        # In test scripts, you can specify --testbed-file argument to run

        # Pick the device, e.g. "my_device" from the testbed.
        device_name = list(self.testbed.devices.keys())[0]
        self.device = self.testbed.devices[device_name]

        self.device.connect()
        self.log.info(f"Connected to device: {device_name}")

    def execute_command(self, command):
        """
        Utility method to execute CLI command and return the output.
        """
        self.log.info(f"Executing command: {command}")
        output = self.device.execute(command)
        self.log.info(f"Command output:\n{output}")
        return output

    @cleanup
    def disconnect_from_device(self):
        """
        Cleanup step: Disconnect from device
        """
        if self.device.is_connected():
            self.device.disconnect()
            self.log.info("Disconnected from device")
