# Standard
import requests
import math
import os
import shutil
import inspect
import time
import logging
from pprint import pformat
from requests.exceptions import *
# Local
from common.constants import *


log = logging.getLogger(__name__)
logging.basicConfig(format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M",)
log.setLevel("DEBUG")


def automation_status(state, test_name, test_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            wrapper_test_name = wrapper.__name__
            wrapper_test_id = wrapper.__dict__.get('test_id', None)
            final_test_name = test_name or wrapper_test_name
            final_test_id = test_id or wrapper_test_id
            log.debug(f"Test State: {state}, Test Name: {final_test_name}, Test ID: {final_test_id}")
            result = func(
                case_id=final_test_id,
                test_name=final_test_name,
                *args,
                **kwargs)
            return result
        return wrapper
    return decorator


def print_endpoint_payload(url: str = "", payload: dict = None) -> None:
    try:
        log.debug(f"Endpoint: {url}\nPayload: {pformat(payload)}")
    except Exception as e:
        log.debug(f"{e}")


def parse_wait_time(wait_time_string: str) -> int:
    """
    Calculate the wait time (in seconds) before the desired
    DUT (device under test) may be used for automation testing.
    Return the wait time.
    """
    index = len(wait_time_string) - 1
    wait_time = ""
    while wait_time_string[index] != " ":
        wait_time = wait_time + wait_time_string[index]
        index = index - 1
    return int(wait_time) * 60


def claim_dut(execution_time: str = "90") -> str:
    """
    Claim the desired device under test (DUT).
    """
    pipeline_job_id = get_job_id()
    if pipeline_job_id < 0:
        return ""

    json_data = {
        "unit": "sit_acceptance_stations",
        "execution_time": execution_time,
        "job_id": pipeline_job_id
    }

    try:
        print_endpoint_payload(USE_SIT_1_ENDPOINT, json_data)
        response = requests.put(url=USE_SIT_1_ENDPOINT, json=json_data).json()
    except Exception as e:
        log.debug(f"{get_function_name()}: {e}")
    else:
        log.debug(f"{get_function_name()}: {response}")
        return response


def create_new_testrail_run() -> int:
    """
    Create a new TestRail Test Run and return the newly created Test Run's ID.
    """
    new_run_id = INVALID_RUN_ID

    if get_gitlab_branch() != "main":
        log.debug(f"{get_function_name()}: Not running on the main branch! Test run will not be created.")
        return new_run_id

    json_data = {
        "id": PROJECT_ID,
        "pipeid": get_job_id(),
        "automation_type": "Acceptance",
        "version": get_sonic_version()
    }

    try:
        print_endpoint_payload(CREATE_NEW_TESTRAIL_RUN_ENDPOINT, json_data)
        response = requests.post(url=CREATE_NEW_TESTRAIL_RUN_ENDPOINT, json=json_data).json()
        log.debug(f"{get_function_name()}: {response}")
        new_run_id = response["run_id"]
    except (ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException, JSONDecodeError, KeyError) as e:
        log.debug(f"{get_function_name()}: {e}")
    else:
        log.debug(f"{get_function_name()}: New TestRail run with run ID {new_run_id} has been created.")
    return new_run_id


def get_project_home_directory() -> str:
    """
    Return the root/home directory of the current project.
    Example: "/home/admin/Git/my_gitlab_project"
    """
    project_home_directory = ""
    try:
        project_home_directory = os.environ["PROJECT_HOME_DIRECTORY"]
    except KeyError as e:
        log.debug(f"{get_function_name()}: {e}")
        project_home_directory = os.path.dirname(os.path.abspath(__file__))
        project_home_directory = project_home_directory.split("/")[:-1]
        project_home_directory = "/".join(project_home_directory)
        os.environ["PROJECT_HOME_DIRECTORY"] = project_home_directory
    finally:
        log.debug(f"{get_function_name()}: project_home_directory - {project_home_directory}")
    return project_home_directory


def create_test_suite_artifacts_directory(test_suite_path_id: str = None) -> None:
    """
    Create a new artifacts directory. If the directory already exists,
    delete it anyway and create a new one.
    """
    if os.path.exists(f"./{ARTIFACTS_DIRECTORY}/{test_suite_path_id}"):
        shutil.rmtree(f"./{ARTIFACTS_DIRECTORY}/{test_suite_path_id}")
    os.mkdir(f"./{ARTIFACTS_DIRECTORY}/{test_suite_path_id}")


def get_function_name() -> str:
    """
    (Helper function) Get the name of the caller function from the stack trace.
    Example: get_job_id() calls get_function_name() -> "get_job_id" is returned.
    """
    return inspect.stack()[1].function + "()"


def get_current_logfile(root_path=None):
    """
    Get the current test-suite-in-execution's log file.
    Example: sonic-cli-1720651360.log
    """
    latest_log_file = LOGFILE_PREFIX + "0" + LOGFILE_SUFFIX

    file_a_id = latest_log_file[len(LOGFILE_PREFIX):-1 * len(LOGFILE_SUFFIX)]
    with os.scandir(root_path) as it:
        for curr_file in it:
            if curr_file.name.__contains__(LOGFILE_PREFIX):
                file_b_id = curr_file.name[len(LOGFILE_PREFIX):-1 * len(LOGFILE_SUFFIX)]
                if file_b_id > file_a_id:
                    latest_log_file = curr_file.name

    return latest_log_file


def get_job_id() -> int:
    """
    Fetch the GitLab job ID if the script is running from the pipeline.
    If the script is not running via the GitLab pipeline, an invalid
    JOB ID will be provided so the script can continue to run.
    """
    try:
        pipeline_job_id = int(os.environ["CI_JOB_ID"])
    except (TypeError, KeyError) as e:
        log.debug(f"{get_function_name()}: {type(e).__name__}, {e} -> Not running from the pipeline!")
        pipeline_job_id = INVALID_JOB_ID
    else:
        log.debug(f"{get_function_name()}: Pipeline job ID fetched - {pipeline_job_id}")
    return pipeline_job_id


def get_run_id() -> int:
    """
    Fetch the current TestRail test run ID.
    """
    try:
        run_id = os.environ["RUN_ID"]
    except KeyError as e:
        log.debug(f"{get_function_name()}: {e}")
        run_id = INVALID_RUN_ID
    else:
        log.debug(f"{get_function_name()}: Run ID fetched - {run_id}")
    return run_id


def get_test_suite_name(test_suite: str = None) -> str:
    """
    Return the name of the test suite file without the extension
    suffix (.py) or the path prefix (/home/Documents/).
    Example: "/tests/Interfaces/test_interfaces.py" --> "test_interfaces"
    """
    test_suite_name = None
    if test_suite:
        test_suite_name = test_suite.split("/")[-1].split(".")[0]
    return test_suite_name


def get_test_suite_path_name(test_suite: str = None) -> str:
    """
    Return the name of the test suite path without path characters
    such as "." or "/".
    Example: "tests/scripts/Interfaces/test_interfaces.py" --> "tests-interfaces-test_interfaces"
    """
    test_suite_path_name = None
    if test_suite:
        test_suite_path_name = test_suite.lower().split("/")
        test_suite_path_name = "-".join(test_suite_path_name)
        test_suite_path_name = test_suite_path_name.split(".")[0]
    return test_suite_path_name


def create_root_artifacts_directory(artifacts_directory: str = ARTIFACTS_DIRECTORY) -> None:
    """
    Create a root artifacts directory if it does not exist. If the artifacts directory already exists,
    the standard os function mkdir() will raise a FileExistsError.
    """
    log.debug(f"{get_function_name()}: Provided artifacts directory - {artifacts_directory}")
    full_path_artifacts_directory = get_project_home_directory() + "/" + artifacts_directory
    try:
        log.debug(f"{get_function_name()}: Creating artifacts directory {full_path_artifacts_directory}")
        os.mkdir(full_path_artifacts_directory)
    except FileExistsError as e:
        log.debug(f"{get_function_name()}: {full_path_artifacts_directory} already exists! -> {e}")
    except FileNotFoundError as e:
        log.debug(f"{get_function_name()}: Parent directory does not exist or provided path is invalid! -> {e}")
    else:
        log.debug(f"Successfully created artifacts directory")
        os.listdir(full_path_artifacts_directory)


def print_environment_variables(dotenv_file: str = None) -> None:
    try:
        log.debug(f"{get_function_name()}")
        log.debug("\n\n--------START READ--------\n\n")
        with open(dotenv_file, "r") as f:
            while True:
                curr_line = f.readline()
                if curr_line == "":
                    break
                log.debug(f"{curr_line}")
        log.debug("\n\n--------END READ--------\n\n")
    except Exception as e:
        log.debug(f"{get_function_name()}: {e}")


def update_environment_variables(dotenv_file: str = None, shared_dict = None) -> None:
    """
    Update the environment variables with data collected during the test automation execution.
    These environment variables will be stored in a .env file and accessed during the email-results
    GitLab CI pipeline stage, where the data will be processed and emailed to people on a whitelist.
    """
    try:
        log.debug(f"{get_function_name()}")

        log.debug("Printing shared_dict items...")
        for key, value in shared_dict.items():
            log.debug(f"{key}={value}")

        log.debug(f"{get_function_name()}: Writing shared_dict data to the dotenv file {dotenv_file}")
        with open(dotenv_file, "w") as f:
            f.write("DUT_IP=" + shared_dict["DUT_IP"])
            f.write("SM_SONIC_INSTALLER_URL=" + shared_dict["SM_SONIC_INSTALLER_URL"])
            f.write("PROJECT_ID=" + shared_dict["PROJECT_ID"] + "\n")
            f.write("RUN_ID=" + shared_dict["RUN_ID"] + "\n")
            f.write("TOTAL_TEST_CASES=" + str(shared_dict["TOTAL_PASSED"] + shared_dict["TOTAL_FAILED"]) + "\n")
            f.write("TOTAL_PASSED=" + str(shared_dict["TOTAL_PASSED"]) + "\n")
            f.write("TOTAL_FAILED=" + str(shared_dict["TOTAL_FAILED"]) + "\n")
            f.write("EXECUTION_FAILURE=" + str(shared_dict["EXECUTION_FAILURE"]) + "\n")
    except TypeError as e:
        log.debug(f"{get_function_name()}: {e}")


def release_product(unit: str = "sit_acceptance_stations", ip: str = "") -> None:
    """
    Release the DUT from automation testing.
    """
    json_data = {
        "model": unit,
        "ip": ip
    }

    try:
        if len(ip) == 0:
            for station_ip in ACCEPTANCE_STATIONS:
                json_data["ip"] = station_ip
                print_endpoint_payload(RELEASE_PRODUCT_ENDPOINT, json_data)
                response = requests.put(url=RELEASE_PRODUCT_ENDPOINT, json=json_data).json()
                log.debug(f"{get_function_name()}: {response}")
    except Exception as e:
        log.debug(f"{get_function_name()}: {e}")


def get_sonic_installer_url() -> str:
    """
    Get the full URL of the currently installed SONiC build image.
    Retrieves the URL from the environment variables.
    Example: http://10.16.1.41:8081/artifactory/sm-sonic-db-local/sonic/cp-202305-v2-dev/cp-202305-v2-dev-1860/sonic-canoga.cp-202305-v2-dev-1860.bin
    """

    sonic_image_url = ""
    try:
        sonic_image_url = os.environ["SM_SONIC_INSTALLER_URL"]
    except (KeyError, Exception) as e:
        log.debug(f"{get_function_name()}: {e}")
    log.debug(f"{get_function_name()}: {sonic_image_url}")
    return sonic_image_url


def get_sonic_version(url: str = get_sonic_installer_url()) -> str:
    """
    Sanitize the SONiC build image URL for readability.
    Can provide
    Example: SONiC_1288
    """
    sonic_image_url = url

    if len(sonic_image_url) == 0:
        return "EXECUTION_FAILURE-DEVICE_OFFLINE"

    sonic_image = "SONiC_" + sonic_image_url.split("/")[-2].split("-")[-1]
    log.debug(f"{get_function_name()}: {sonic_image}")
    return sonic_image


def create_ticket_on_failure(test_case_title: str = "NULL",
                             test_case_id: int = INVALID_CASE_ID,
                             path_to_log: str = None) -> None:
    """
    Update the current automation test run on Testrail with a failing test case.
    Include a .txt log file to be uploaded and attached to the failing test case.

    This function, unlike test_case_failed(), will create a GitLab ticket in
    addition to failing the test case on Testrail.
    """
    # Update TestRail
    json_data = {
        "run_id": get_run_id(),
        "project_id": GITLAB_SIT_AUTOMATION_PROJ_ID,
        "test_case_title": test_case_title,
        "test_case_id": test_case_id,
        "path": path_to_log,
        "version": get_sonic_version(),
        "branch": get_gitlab_branch(),
        "job_id": get_job_id()
    }

    try:
        print_endpoint_payload(CREATE_ISSUE_UPON_TEST_FAIL_ENDPOINT, json_data)
        response = requests.post(url=CREATE_ISSUE_UPON_TEST_FAIL_ENDPOINT, json=json_data).json()
    except ConnectionError as e:
        log.debug(f"{get_function_name()}: {e}")
    else:
        log.debug(f"{get_function_name()}: {response}")


def test_case_failed(case_id: int = INVALID_CASE_ID, elapsed: float = 0.0, file = None) -> None:
    """
    Update the current automation test run on Testrail with a failing test case.
    Include a .txt log file to be uploaded and attached to the failing test case.
    """
    # Update TestRail
    with open(file, "r") as f:
        file_content = f.read()
        json_data = {
            "run_id": get_run_id(),
            "case_id": case_id,
            "elapsed": str(math.ceil(elapsed)) + "s",
            "file_content": file_content,
            "version": get_sonic_version()
        }

        try:
            print_endpoint_payload(FAIL_TEST_CASE_ENDPOINT, json_data)
            response = requests.post(url=FAIL_TEST_CASE_ENDPOINT, json=json_data).json()
        except ConnectionError as e:
            log.debug(f"{get_function_name()}: {e}")
        else:
            log.debug(f"{get_function_name()}: {response}")


def test_case_passed(case_id: int = INVALID_CASE_ID, elapsed: float = 0.0, file = None) -> None:
    """
    Update the current automation test run on Testrail with a passing test case.
    Include a .txt log file to be uploaded and attached to the passing test case.
    """
    # Update TestRail
    with open(file, "r") as f:
        file_content = f.read()
        json_data = {
            "run_id": get_run_id(),
            "case_id": case_id,
            "elapsed": str(math.ceil(elapsed)) + "s",
            "file_content": file_content
        }

        try:
            print_endpoint_payload(PASS_TEST_CASE_ENDPOINT, json_data)
            response = requests.post(url=PASS_TEST_CASE_ENDPOINT, json=json_data).json()
        except ConnectionError as e:
            log.debug(f"{get_function_name()}: {e}")
        else:
            log.debug(f"{get_function_name()}: {response}")


def upload_text_file(file_path=None) -> None:
    """
    Upload a .txt file to the SIT VM.
    """
    file = {"file": open(file_path, "rb")}

    try:
        response = requests.post(url=UPLOAD_TEXT_FILE_ENDPOINT, files=file).json()
    except ConnectionError as e:
        log.debug(f"{get_function_name()}: {e}")
    else:
        log.debug(f"{get_function_name()}: {response}")


def get_gitlab_branch() -> str:
    """
    (GitLab pipeline) Fetch the current gitlab branch.
    """
    branch = ""
    try:
        log.debug(f"{get_function_name()}: Fetching current branch name...")
        branch = os.environ["CI_COMMIT_REF_NAME"]
        log.debug(f"{get_function_name()}: Commit branch - {branch}")
    except KeyError as e:
        log.debug(f"{get_function_name()}: {e}, -> Not running from the pipeline!")
    return branch
