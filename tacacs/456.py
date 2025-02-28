import logging
from pyats import aetest
from pyats.topology import loader
from unicon.core.errors import SubCommandFailure

logger = logging.getLogger(__name__)

class helloTest(aetest.Testcase):
    """Common Setup section to load testbed and establish connections."""

    @aetest.setup
    def setup(self, testbed):
        """
        Connect to both the admin and test_user devices.
        """
        # Store references in testscript parameters for later usage
        # self.parent.parameters['admin_device'] = testbed.devices['admin_device']
        self.parent.parameters['test_user_device'] = testbed.devices['test_user_device']
        
        # logger.info("Connecting to admin_device...")
        # self.parent.parameters['admin_device'].connect()
        
        logger.info("Connecting to test_user_device...")
        self.parent.parameters['test_user_device'].connect()



    @aetest.test
    def show_tacacs_configuration(self, test_user_device):
        """
        Run 'show tacacs' (or equivalent commands) on the test_user device.
        """
        logger.info("Showing TACACS configuration on test_user_device...")
        try:
            # Adjust this command to your environment’s actual CLI/shell command.
            output = test_user_device.execute("show tacacs")
            logger.debug(f"'show tacacs' output:\n{output}")
            
            # Add validation logic as needed, for example:
            if "TACPLUS_SERVER" not in output:
                self.failed("TACACS service does not appear to be running!")
        except SubCommandFailure as e:
            self.failed(f"Failed to get TACACS info from test_user_device. Reason:\n{str(e)}")
        else:
            self.passed("Successfully verified TACACS status on test_user_device.")


    @aetest.cleanup
    def cleanup(self):
        self.parent.parameters['test_user_device'].disconnect()
        logger.info("Cleanup steps go here, if necessary (e.g., stopping services).")