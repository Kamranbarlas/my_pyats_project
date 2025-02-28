import inspect

RUN_ID: int = 787

CONFIG_COMMANDS = {
    "config aaa": 7353
}

SHOW_COMMANDS = {
    "show aaa": 517,
    "show acl rule": 518,
    "show acl table": 0,
    "show arp": 519,
    "show auto-techsupport global": 7329,
    "show auto-techsupport history": 0,
    "show auto-techsupport-feature": 7330,
    "show bfd peer": 7332,
    "show bfd summary": 0,
    "show boot": 7087,
    "show buffer configuration": 7252,
    "show buffer information": 0,
    "show buffer_pool persistent-watermark": 7331,
    "show buffer_pool watermark": 0,
    "show chassis": 7333,
    "show clock": 7085,
    "date": 0,
    "show dropcounters capabilities": 7369,
    "show dropcounters configuration": 0,
    "show dropcounters counts": 0,
    "show ecn": 7370,
    "show environment": 7371,
    "show feature": 7250,
    "show interfaces alias": 7251,
    "show interfaces autoneg status": 0,
    "show interfaces breakout": 0,
    "show interfaces counters": 0,
    "show interfaces description": 0,
    "show interfaces link-training status": 0,
    "show interfaces mpls": 0,
    "show interfaces naming_mode": 0,
    "show interfaces neighbor expected": 0,
    "show interfaces portchannel": 0,
    "show interfaces status": 0,
    "show interfaces tpid": 0,
    "show interfaces transceiver eeprom": 0,
    "show interfaces transceiver error-status": 0,
    "show interfaces transceiver info": 0,
    "show interfaces transceiver lpmode": 0,
    "show interfaces transceiver pm": 0,
    "show interfaces transceiver presence": 0,
    "show interfaces transceiver status": 0,
    "show kubernetes labels": 0,
    "show kubernetes server config": 0,
    "show kubernetes server status": 0,
    "show line": 7088,
    "show logging": 7089,
    "show storm-control": 7249,
    "show uptime": 0,
    "show users": 7248,
    "show version": 7086,
    "show processes": 7352,
    "show warm_restart": 0,
    "show watermark": 0,
    "show ztp": 7084,
}

# STATUS_IDS = {
#     "Passed": 1,
#     "Blocked": 2,
#     "Retest": 4,
#     "Failed": 5
# }


def get_test_show_command_name() -> str:
    caller_func_name = inspect.stack()[1][3]

    # test_show_feature_config -> show_feature_config
    caller_func_name = caller_func_name[5:]
    caller_func_name = caller_func_name.split("_")
    return " ".join(caller_func_name)
