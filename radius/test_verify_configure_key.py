from pyats import aetest
from pyats.topology import loader
import logging

class VerifyConfigureKeyRadiusServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def verify_configuring_radius_key(self):
        """Verify that setting the shared key for the RADIUS server works correctly."""
        # Define the RADIUS server IP and the passkey value.
        server_ip = "10.16.9.112"  # Replace with the actual RADIUS server IP address
        passkey = "Scientist123"  # Replace with the actual passkey value
        
        # Construct the command to add/update the RADIUS server with the shared key.
        # Note: The command format may vary based on your device; adjust accordingly.
        command = f"sudo config radius add {server_ip} {passkey}"
        logging.info(f"Executing command to configure the RADIUS shared key: {command}")
        
        # Execute the command on the device.
        output = self.device.execute(command)
        logging.info(f"Output from command execution:\n{output}")
        
        # Validate that the command was successful.
        # Adjust the success condition based on the actual expected output from your device.
        if "success" not in output.lower():
            self.failed(f"Failed to update the shared key. Output: {output}")
        else:
            self.passed("Shared key updated successfully for the RADIUS server.")




    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()