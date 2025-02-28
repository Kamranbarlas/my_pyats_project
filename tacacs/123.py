import logging
from pyats import aetest
from pyats.topology import loader
from unicon.core.errors import SubCommandFailure

logger = logging.getLogger(__name__)

class hello1(aetest.Testcase):
    """Common Setup section to load testbed and establish connections."""

    @aetest.setup
    def setup(self, testbed):
        """
        Connect to both the admin and test_user devices.
        """
        # Store references in testscript parameters for later usage
        self.parent.parameters['admin_device'] = testbed.devices['admin_device']
        # self.parent.parameters['test_user_device'] = testbed.devices['test_user_device']
        
        logger.info("Connecting to admin_device...")
        self.parent.parameters['admin_device'].connect()
        
        # logger.info("Connecting to test_user_device...")
        # self.parent.parameters['test_user_device'].connect()



    @aetest.test
    def configure_tacacs_server(self, admin_device):
        """
        Configure the TACACS server on the admin device.
        Modify the CLI commands to match your actual TACACS setup.
        """
        logger.info("Configuring TACACS server on admin_device...")
        try:
            # Example commands: these will vary based on your environment
            # For instance, if you are on a Linux shell, you'd do something
            # relevant to your TACACS daemon configuration.
            config_commands = [
                "sudo config aaa authentication login tacacs+ local",
                "sudo config aaa authentication fallback enable",   
                "sudo config tacacs add 10.16.9.110 testing123",
                # "sudo systemctl enable tacacs",
                # Additional configuration or checks as needed
            ]
            for cmd in config_commands:
                output = admin_device.execute(cmd)
                print("*"*100, output)
                logger.debug(f"Executed '{cmd}', output:\n{output}")
        except SubCommandFailure as e:
            self.failed(f"Failed to configure TACACS on admin_device. Reason:\n{str(e)}")
        else:
            self.passed("Successfully configured TACACS on admin_device.")



    @aetest.cleanup
    def cleanup(self):
        self.parent.parameters['admin_device'].disconnect()
        logger.info("Cleanup steps go here, if necessary (e.g., stopping services).")