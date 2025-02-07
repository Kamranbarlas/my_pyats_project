# jobs/radius_job.py

import os
from pyats.easypy import run

def main(runtime):
    """
    This job file runs only the RADIUS tests.
    """
    import pdb;pdb.set_trace()
    test_script = os.path.join('auth_tests', 'radius_tests.py')
    run(
            testscript=test_script,
            runtime=runtime,
            on_fail='abort'
        )
