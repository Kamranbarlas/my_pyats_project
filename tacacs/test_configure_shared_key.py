from pyats import aetest
from pyats.topology import loader

class ConfigureSharedKeyTacacsServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def configure_shared_key_tacacs_server(self):
        """Configure Shared Key for a TACACS server."""
        shared_key = "Scientist123" 
        command = f"sudo config tacacs shared_key {shared_key}"
        output = self.device.execute(command)
        if "success" not in output.lower():
            self.failed(f"Failed to add shared_key to TACACS server. Output: {output}")
        else:
            self.passed("TACACS server shared_key added successfully.")


    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()