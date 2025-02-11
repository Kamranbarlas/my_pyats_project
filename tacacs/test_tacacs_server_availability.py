from pyats import aetest
from pyats.topology import loader

class AvailabliltyTacacsServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def Availability_tacacs_server(self):
        """
        Verify that default TACACS config shows no servers configured.
        """
        output = self.device.execute("show tacacs")
        # Check if the output indicates no TACACS servers configured
        # This will depend on device output
        if "No TACACS server configured" in output or "TACPLUS" in output:
            self.passed("Default TACACS config has no servers configured.")
        else:
            self.failed("Expected no servers in default TACACS config, but found otherwise.")


    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()