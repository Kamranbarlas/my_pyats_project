# from pyats.easypy import run
# from auth_tests import list_test_scripts

# def main(runtime):
#     test_scripts = list_test_scripts()  # get them in the desired order

#     for script in test_scripts:
#         # By default, each run() is synchronous — it won’t move on until the test finishes.
#         # on_fail='abort' tells Easypy to stop execution of subsequent tasks if this one fails.
#         run(
#             testscript=script,
#             runtime=runtime,
#             on_fail='abort'
#         )


import os
from pyats.easypy import run
import radius

def main(runtime):
    """
    This job file runs only the RADIUS tests.
    """
    # import pdb;pdb.set_trace()
    test_scripts = radius.list_test_scripts()
    print("Discovered scripts:", test_scripts)

    for script in test_scripts:
        # By default, each run() is synchronous — it won’t move on until the test finishes.
        # on_fail='abort' tells Easypy to stop execution of subsequent tasks if this one fails.
        run(
            testscript=script,
            runtime=runtime,
            on_fail='abort'
        )

