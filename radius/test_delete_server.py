from pyats import aetest
from pyats.topology import loader

class DeleteRadiusServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def delete_radius_server(self):
        """Delete a RADIUS server."""
        server_ip = "10.16.9.112"  # Replace with your RADIUS server IP
        command = f"sudo config radius delete {server_ip}"
        output = self.device.execute(command)
        if "success" not in output.lower():
            self.failed(f"Failed to delete RADIUS server. Output: {output}")
        else:
            self.passed("RADIUS server deleted successfully.")


    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()