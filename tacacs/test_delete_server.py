from pyats import aetest
from pyats.topology import loader

class DeleteTacacsServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def delete_tacacs_server(self):
        """Delete a TACACS server."""
        server_ip = "10.16.9.112"
        output = self.device.execute("show tacacs")
        if server_ip in output: 
            command = f"sudo config tacacs delete {server_ip}"
            self.device.execute(command)
        check = self.device.execute("show tacacs")
        if server_ip in check:
            self.failed(f"Failed to delete TACACS server. Output: {output}")
        else:
            self.passed("TACACS server delete successfully.")

    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()