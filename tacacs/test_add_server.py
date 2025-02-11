from pyats import aetest
from pyats.topology import loader

class AddTacacsServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def add_tacacs_server(self):
        """Add a TACACS server."""
        server_ip = "10.16.9.112"  # Replace with your TACACS server IP
        command = f"sudo config tacacs add {server_ip} testing123"
        output = self.device.execute(command)
        check = self.device.execute("show tacacs")
        if server_ip not in check:
            self.failed(f"Failed to add TACACS server. Output: {output}")
        else:
            self.passed("TACACS server added successfully.")

    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()