from pyats import aetest
from pyats.topology import loader
import logging, time

log = logging.getLogger(__name__)
class MultipleRadiusServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def verify_multiple_radius_servers(self):
        """Verify that multiple RADIUS servers can be configured in the system."""
        # Define the RADIUS server IPs and shared secret
        server1_ip = "10.16.9.119"
        server2_ip = "10.16.9.120"  # Replace with your RADIUS server IP
        command = f"sudo config radius add {server1_ip} testing123"
        
        output = self.device.execute(command)
        print("output===========",output)
        # if "success" not in output.lower():
        #     self.failed(f"Failed to add RADIUS server. Output: {output}")
        # else:
        #     self.passed("RADIUS server added successfully.")
        time.sleep(10)
        command = f"sudo config radius add {server2_ip} testing123"
        output = self.device.execute(command)
        print("output===========",output)

        command = f"show radius"
        output = self.device.execute(command)
        if server1_ip and server2_ip not in output.lower():
            self.failed(f"Failed to add RADIUS server. Output: {output}")
        else:
            self.passed("RADIUS server added successfully.")

        # Verify that both server IPs are present in the output
        # if server1_ip not in show_output or server2_ip not in show_output:
        #     self.failed(
        #         f"RADIUS configuration verification failed. "
        #         f"Both servers not found in output:\n{show_output}"
        #     )
        # else:
        #     self.passed("Both RADIUS servers are configured and active.")



    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()