from pyats import aetest
from pyats.topology import loader
import logging

logger = logging.getLogger(__name__)
class AvailabliltyTacacsServerTest(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
       
       logger.info("Connecting to admin_device...")
       self.parent.parameters['admin_device'] = testbed.devices['admin_device']
       self.parent.parameters['admin_device'].connect()

        #Connect to both the admin and test_user devices.


    @aetest.test
    def Availability_tacacs_server(self,admin_device):
        """
        Verify that default TACACS config shows no servers configured.
        """
        output = admin_device.device.execute("show tacacs")
        # Check if the output indicates no TACACS servers configured
        # This will depend on device output
        if "No TACACS server configured" in output or "TACPLUS" in output:
            self.passed("Default TACACS config has no servers configured.")
        else:
            self.failed("Expected no servers in default TACACS config, but found otherwise.")


    @aetest.cleanup
    def cleanup(self):
        """Disconnect from the device."""
        self.parent.parameters['admin_device'].disconnect()
        logger.info("Cleanup steps go here, if necessary (e.g., stopping services).")