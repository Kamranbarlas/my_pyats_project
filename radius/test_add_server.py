from pyats import aetest
from pyats.topology import loader

class AddRadiusServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def add_radius_server(self):
        """Add a RADIUS server."""
        server_ip = "10.16.9.112"  # Replace with your RADIUS server IP
        command = f"sudo config radius add {server_ip}"
        output = self.device.execute(command)
        print("output===========",output)
        if "success" not in output.lower():
            self.failed(f"Failed to add RADIUS server. Output: {output}")
        else:
            self.passed("RADIUS server added successfully.")

    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()