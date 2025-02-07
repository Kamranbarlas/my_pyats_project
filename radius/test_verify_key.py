from pyats import aetest
from pyats.topology import loader
import logging

class VerifyKeyRadiusServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device."""
        self.device = testbed.devices['linux_server']
        self.device.connect()

    @aetest.test
    def verify_radius_key_configuration(self):
        """Verify the shared key configuration for the RADIUS server."""
        # Execute the 'show radius' command to retrieve the current configuration.
        command = "show radius"
        logging.info(f"Executing command: {command}")
        output = self.device.execute(command)
        logging.info(f"'show radius' output:\n{output}")

        # Verification Approach:
        # Option 1: The shared key might be masked (e.g., "******" or "hidden") for security.
        # Option 2: The shared key might be explicitly shown (if configured to do so).
        #
        # Adjust these conditions based on your device's behavior.
        masked_indicators = ["******", "hidden"]
        expected_passkey = "your_passkey_here"  # Replace with the expected passkey if the key is shown

        # Check if the output indicates that the key is masked
        key_masked = any(indicator in output for indicator in masked_indicators)

        # Check if the key is explicitly displayed (if that's expected)
        key_displayed = expected_passkey in output

        if key_masked:
            logging.info("Shared key appears to be hidden (masked) for security purposes.")
            self.passed("Shared key configuration is correct and hidden as expected.")
        elif key_displayed:
            logging.info("Shared key is correctly displayed as expected.")
            self.passed("Shared key configuration is correct and visible as expected.")
        else:
            self.failed("Shared key configuration verification failed. The shared key is neither correctly hidden nor correctly displayed.")





    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.device.disconnect()