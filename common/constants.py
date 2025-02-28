from enum import Enum

# TestRail
INVALID_RUN_ID = -1
INVALID_CASE_ID = -1
TEST_CASE_FAILED = 0
TEST_CASE_PASSED = 1
PROJECT_ID = 1
PROJECT_NAME = "SyncMetra"


class Result(Enum):
    PASSED = 1
    BLOCKED = 2
    RETEST = 4
    FAILED = 5


RESULT = {
    "Passed": 1,
    "Blocked": 2,
    "Retest": 4,
    "Failed": 5
}

"""
Test case types
- Acceptance
- Accessibility
- Compatibility
- Functional
- Negative
- Other
- Performance
- Scalability
- Security
- Startup Shutdown
- Usability
"""

# GitLab
ARTIFACTS_DIRECTORY = "reports"
LOCAL_ENVIRONMENT = "testrail_run.env"
TEST_SUITE_DIRECTORY = "tests/scripts"
INVALID_JOB_ID = -1
GITLAB_SIT_PYATS_PROJ_ID = 811
GITLAB_SIT_AUTOMATION_PROJ_ID = 768


DEFAULT_DEVICE_NAME = "sm100"


# pyATS
EXECUTING = "Executing command: "
CONFIGURE = "Configuring device"
EXEC_PARSE = "Executing and parsing output"
VALIDATE = "Validating output"
DELETE = "Deleting configuration"
UPDATE = "Updating configuration"
NOT_CONNECTED = "No device connection detected!"
LOGFILE_PREFIX = "sonic-cli-"
LOGFILE_SUFFIX = ".log"
SIT_1 = "10.16.9.77"
SIT_10 = "10.16.9.82"
ACCEPTANCE_STATIONS = [SIT_1, SIT_10]
TIMEOUT_5_SEC = 5
TIMEOUT_20_SEC = 20
TIMEOUT_30_SEC = 30
TIMEOUT_1_MIN = 60
TIMEOUT_5_MIN = 300
IXTCL_PATH = "/opt/Ixia/ixos-api/8.00.0.5/bin/ixtcl"
EXECUTION_TIME = 160


EMAILS = [
    "araval@canogaperkins.net",
    "shannay@canogaperkins.net",
    "gespinosa@canogaperkins.net",
    "jeffrie@canogaperkins.net",
    "jromero@canogaperkins.net"
]


# Test ports
TEST_PORT_1 = "Ethernet16"
TEST_PORT_2 = "Ethernet26"
TEST_PORT_3 = "Ethernet18"
TEST_PORTS = [TEST_PORT_1, TEST_PORT_2]

PORT_LIST = [
    # lc 0
    "Ethernet0",
    "Ethernet1",
    "Ethernet2",
    "Ethernet3",
    "Ethernet4",
    "Ethernet5",
    "Ethernet6",
    "Ethernet7",
    "Ethernet8",
    "Ethernet9",
    "Ethernet10",
    "Ethernet11",
    "Ethernet12",
    "Ethernet13",
    "Ethernet14",
    "Ethernet15",
    # lc 1
    "Ethernet16",
    "Ethernet17",
    "Ethernet18",
    "Ethernet19",
    "Ethernet20",
    "Ethernet21",
    "Ethernet22",
    "Ethernet23",
    "Ethernet24",
    "Ethernet25",
    "Ethernet26",
    "Ethernet27",
    "Ethernet28",
    "Ethernet29",
    "Ethernet30",
    "Ethernet31",
    # lc 2
    "Ethernet32",
    "Ethernet33",
    "Ethernet34",
    "Ethernet35",
    "Ethernet36",
    "Ethernet37",
    "Ethernet38",
    "Ethernet39",
    "Ethernet40",
    "Ethernet41",
    "Ethernet42",
    "Ethernet43",
    "Ethernet44",
    "Ethernet45",
    "Ethernet46",
    "Ethernet47"
]


# REST API endpoints
UPDATE_SONIC_URL_ENDPOINT = "http://172.16.4.209:8082/update_sonic_url"
UPDATE_JOBS_ENDPOINT = "http://172.16.4.209:8081/update_jobs"
USE_SIT_1_ENDPOINT = "http://172.16.4.209:8081/use_sit1"
CREATE_NEW_TESTRAIL_RUN_ENDPOINT = "http://172.16.4.209:8080/create_new_testruner"
RELEASE_PRODUCT_ENDPOINT = "http://172.16.4.209:8081/release"
CREATE_ISSUE_UPON_TEST_FAIL_ENDPOINT = "http://172.16.4.209:8080/create_issue_upon_test_failure"
FAIL_TEST_CASE_ENDPOINT = "http://172.16.4.209:8080/fail_test_case"
PASS_TEST_CASE_ENDPOINT = "http://172.16.4.209:8080/pass_test_case"
UPLOAD_TEXT_FILE_ENDPOINT = "http://172.16.4.209:8080/upload_text_file"
EMAIL_REPORT_ENDPOINT = "http://172.16.4.209:8080/send_pyats_results"
EMAIL_EXECUTION_FAIL_ENDPOINT = "http://172.16.4.209:8080/send_execution_fail_email"
ADD_UNTESTED_BUILD_ENDPOINT = "http://172.16.4.209:8081/add-untested-build"

# Paths
AUTH_LOG_PATH = "/var/log/auth.log"
