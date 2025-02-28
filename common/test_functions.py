# Standard
import logging
from logging.handlers import RotatingFileHandler
import inspect
import os.path
import time
import subprocess
import shutil
from pprint import pprint, pformat
import re
# pyATS
from pyats import aetest
from pyats.easypy import plugins
from pyats.topology import Testbed, Device
from pyats.utils.exceptions import *
from genie.utils import Dq
from pyats.log import TaskLogHandler
import pyats.results
# Local
from common.api_call import *
from common.constants import *
from common.commands import *


log = logging.getLogger(__name__)
logging.basicConfig(format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")
log.setLevel("DEBUG")


def get_interfaces_status(testbed = None) -> dict:
    try:
        return testbed.parse("show interfaces status")
    except Exception as e:
        log.debug(f"{e}")


def get_vlan_config_database(testbed = None) -> dict:
    try:
        return testbed.parse("show vlan config")
    except Exception as e:
        log.debug(f"{e}")


def get_mac_learning_database(testbed = None) -> dict:
    try:
        return testbed.parse("show mac")
    except Exception as e:
        log.debug(f"{e}")


def get_device_alias(parsed: dict = None) -> str:
    if parsed:
        return list(parsed.keys())[0]
    return "sit-sm100-1"


def set_default_vlan_config(testbed = None) -> None:
    """
    Set the VLAN database to its default configuration.
    """
    try:
        log.debug("Setting VLAN configuration to default...")
        vlan_database = get_vlan_config_database(testbed)
        log.debug(f"Current VLAN config: {vlan_database}")
        dev_alias = list(vlan_database.keys())[0]
        vlans = vlan_database[dev_alias]["vlans"]
        log.debug(f"VLANs: {pformat(vlans)}")

        for vlan in vlans:
            if vlan == "Vlan1":
                continue

            log.debug(f"\nVLAN configuration for {vlan}")
            log.debug(pformat(vlans[vlan]))

            vid = vlans[vlan]["vid"]
            vlan_ports = list(vlans[vlan]["ports"].keys())
            for port in vlan_ports:
                log.debug(f"Removing port membership for {port} in {vlan}...")
                if "S-Vlan" in vlan:
                    testbed.execute(f"sudo config svlan member del {vid} {port}")
                else:
                    testbed.execute(f"sudo config vlan member del {vid} {port}")

            log.debug(f"\nDeleting VLAN {vlan}...")
            if "S-Vlan" in vlan:
                testbed.execute(f"sudo config svlan del {vid}")
            else:
                testbed.execute(f"sudo config vlan del {vid}")
        testbed.execute("show vlan config")
    except (KeyError, Exception) as e:
        log.debug(f"{e}")
        return


def shutdown_port(testbed = None, *argv) -> None:
    try:
        for arg in argv:
            if re.match(r"Ethernet\d+", arg):
                testbed.execute(f"sudo config interface shutdown {arg}")
        testbed.execute("show interfaces status")
    except Exception as e:
        log.debug(f"{e}")


def shutdown_all_test_ports(testbed = None, test_ports: list = TEST_PORTS) -> None:
    try:
        log.debug("Shutting down all test ports...")
        for port in test_ports:
            if re.match(r"Ethernet\d+", port):
                testbed.execute(f"sudo config interface shutdown {port}")
        testbed.execute("show interfaces status")
    except Exception as e:
        log.debug(f"{e}")


def set_all_test_port_speeds(testbed = None, speed: int = 25000, test_ports: list = TEST_PORTS) -> None:
    try:
        log.debug(f"Setting all test port speeds to {speed} Mbps")
        for port in test_ports:
            testbed.execute(f"sudo config interface speed {port} {speed}")
    except Exception as e:
        log.debug(f"{e}")


def get_port_list(testbed = None) -> list:
    try:
        log.debug("Retrieving a list of all ports...")
        parsed_interfaces_status = testbed.parse("show interfaces status")
        dev_alias = get_device_alias(parsed_interfaces_status)
        ports = list(parsed_interfaces_status[dev_alias]["interfaces"].keys())
        return ports
    except Exception as e:
        log.debug(f"{e}")


def shutdown_all_ports(testbed = None) -> None:
    try:
        log.debug("Shutting down all ports...")
        ports = get_port_list(testbed)
        for port in ports:
            if re.match(r"Ethernet\d+", port):
                testbed.execute(f"sudo config interface shutdown {port}")
        testbed.execute("show interfaces status")
    except Exception as e:
        log.debug(f"{e}")


def set_all_port_speeds(testbed = None, speed: int = 25000) -> None:
    try:
        log.debug(f"Setting all port speeds to {speed} Mbps")
        for port in get_port_list(testbed):
            testbed.execute(f"sudo config interface speed {port} {speed}")
        testbed.execute("show interfaces status")
    except Exception as e:
        log.debug(f"{e}")


def clear_mac_learning_database(testbed = None) -> None:
    try:
        log.debug("Clearing the MAC learning database...")
        testbed.execute("sudo sonic-clear fdb all")
        testbed.execute("show mac")
    except Exception as e:
        log.debug(f"{e}")


def clear_all_counters(testbed = None) -> None:
    try:
        log.debug("Clearing all interface counters...")
        testbed.execute("sudo sonic-clear counters")
        testbed.execute("show interfaces counters")
        for port in TEST_PORTS:
            testbed.execute(f"show interfaces counters detailed {port}")
    except Exception as e:
        log.debug(f"{e}")


def set_default_device_config(testbed = None) -> None:
    """
    Resets the VLAN configuration, shuts down all active ports (admin UP),
    sets all port speeds to 25G, clears the MAC learning database,
    and clears all port counter statistics.
    """
    try:
        set_default_vlan_config(testbed)

        shutdown_all_ports(testbed)

        set_all_port_speeds(testbed)

        clear_mac_learning_database(testbed)

        clear_all_counters(testbed)

        set_default_tacacs_config(testbed)

        set_interface_naming_mode(testbed)

        set_default_radius_config(testbed)

        set_default_aaa_config(testbed)
    except Exception as e:
        log.debug(f"{e}")


def test_port_speeds(testbed = None, port = "", expected_speed = 0) -> bool:
    try:
        interfaces_status = get_interfaces_status(testbed)
        parsed_port_speed = Dq(interfaces_status).contains(port).get_values("speed", 0)
        if parsed_port_speed != expected_speed:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def test_port_startup(testbed = None, port = "", expected_admin = "") -> bool:
    try:
        interfaces_status = get_interfaces_status(testbed)
        parsed_port_admin_status = Dq(interfaces_status).contains(port).get_values("admin", 0)
        if parsed_port_admin_status != expected_admin:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def test_vlan_was_added(testbed = None, expected_vid = 0) -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_vid = Dq(vlan_database).contains(f"Vlan{expected_vid}").get_values("vid", 0)
        if parsed_vid != expected_vid:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def test_svlan_was_added(testbed = None, expected_svid = 0) -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_svid = Dq(vlan_database).contains(f"S-Vlan{expected_svid}").get_values("vid", 0)
        if parsed_svid != expected_svid:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def test_if_vlan_member(testbed = None, vid = 0, port = "") -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        print(vlan_database)
        parsed_port_members = Dq(vlan_database).contains(f"Vlan{vid}").get_values("ports")
        print(parsed_port_members)
        if not port in parsed_port_members:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def test_if_svlan_member(testbed = None, vid = 0, port = "") -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_port_members = Dq(vlan_database).contains(f"S-Vlan{vid}").get_values("ports")
        if not port in parsed_port_members:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def test_if_untagged_vlan_member(testbed = None, vid = 0, port = "") -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_port_members = Dq(vlan_database).contains(f"Vlan{vid}").get_values("ports")
        if parsed_port_members[port]["port_tagging"] != "untagged":
            return False
    except (KeyError, Exception) as e:
        log.debug(f"{e}")
        return False
    return True


def test_if_tagged_vlan_member(testbed = None, vid = 0, port = "") -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_port_members = Dq(vlan_database).contains(f"Vlan{vid}").get_values("ports")
        if parsed_port_members[port]["port_tagging"] != "tagged":
            return False
    except (KeyError, Exception) as e:
        log.debug(f"{e}")
        return False
    return True


def test_if_single_tagged_svlan_member(testbed = None, vid = 0, port = "") -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_port_members = Dq(vlan_database).contains(f"S-Vlan{vid}").get_values("ports")
        if parsed_port_members[port]["port_tagging"] != "tagged":
            return False
    except (KeyError, Exception) as e:
        log.debug(f"{e}")
        return False
    return True


def test_if_double_tagged_svlan_member(testbed = None, vid = 0, port = "") -> bool:
    try:
        vlan_database = get_vlan_config_database(testbed)
        parsed_port_members = Dq(vlan_database).contains(f"S-Vlan{vid}").get_values("ports")
        if parsed_port_members[port]["port_tagging"] != "double_tagged":
            return False
    except (KeyError, Exception) as e:
        log.debug(f"{e}")
        return False
    return True


def test_mac_learning(testbed = None, expected_mac = "", expected_port = "", expected_mac_type = "", expected_vid = 0) -> bool:
    try:
        dut_alias = list(testbed.devices.keys())[0]
        mac_database = get_mac_learning_database(testbed)
        print(mac_database)
        search_entry = {'vlan': f'Vlan{expected_vid}', 'mac_address': f'{expected_mac}', 'port': f'{expected_port}', 'type': f'{expected_mac_type}'}
        print(search_entry)
        mac_exists = any(entry == search_entry for entry in mac_database[dut_alias]['mac_table'].values())
        if not mac_exists:
            return False
    except Exception as e:
        log.debug(f"{e}")
        return False
    return True


def get_mac_table_length(mac_table: dict = None) -> int:
    mac_table_len = 0
    if mac_table:
        mac_table_len = len(mac_table[list(mac_table.keys())[0]]['mac_table'])
    return mac_table_len


def get_detailed_int_counters(testbed = None, port: str = "") -> dict:
    if testbed:
        return testbed.parse(f"show interfaces counters detailed {port}")


def print_detailed_int_counters(detailed_int_counters = None) -> None:
    if detailed_int_counters:
        pass


def test_bad_crc_packet_counters(detailed_int_counters: dict = None, expected_count: int = 0) -> bool:
    passed = False
    if detailed_int_counters:
        bad_crc_packet_counters = Dq(detailed_int_counters).contains("errors").get_values("fragments", 0)
        if bad_crc_packet_counters >= expected_count:
            log.debug(f"Parsed counter {bad_crc_packet_counters} matches expected {expected_count}")
            passed = True
    else:
        log.debug(f"Parsed command 'show interfaces counters detailed <PORT>' was not received!")
    return passed


def test_jabber_packet_counters(detailed_int_counters: dict = None, expected_count: int = 0) -> bool:
    passed = False
    if detailed_int_counters:
        jabber_packet_counters = Dq(detailed_int_counters).contains("errors").get_values("jabbers", 0)
        if jabber_packet_counters >= expected_count:
            log.debug(f"Parsed counter {jabber_packet_counters} matches expected {expected_count}")
            passed = True
    else:
        log.debug(f"Parsed command 'show interfaces counters detailed <PORT>' was not received!")
    return passed


def test_fragmented_packet_counters(detailed_int_counters: dict = None, expected_count: int = 0) -> bool:
    passed = False
    if detailed_int_counters:
        fragmented_packet_counters = Dq(detailed_int_counters).contains("errors").get_values("fragments", 0)
        if fragmented_packet_counters >= expected_count:
            log.debug(f"Parsed counter {fragmented_packet_counters} matches expected {expected_count}")
            passed = True
    else:
        log.debug(f"Parsed command 'show interfaces counters detailed <PORT>' was not received!")
    return passed


def test_undersize_packet_counters(detailed_int_counters: dict = None, expected_count: int = 0) -> bool:
    passed = False
    if detailed_int_counters:
        undersize_packet_counters = Dq(detailed_int_counters).contains("errors").get_values("undersize", 0)
        if undersize_packet_counters >= expected_count:
            log.debug(f"Parsed counter {undersize_packet_counters} matches expected {expected_count}")
            passed = True
    else:
        log.debug(f"Parsed command 'show interfaces counters detailed <PORT>' was not received!")
    return passed


def test_overrun_packet_counters(detailed_int_counters: dict = None, expected_count: int = 0) -> bool:
    passed = False
    if detailed_int_counters:
        overrun_packet_counters = Dq(detailed_int_counters).contains("errors").get_values("overruns", 0)
        if overrun_packet_counters >= expected_count:
            log.debug(f"Parsed counter {overrun_packet_counters} matches expected {expected_count}")
            passed = True
    else:
        log.debug(f"Parsed command 'show interfaces counters detailed <PORT>' was not received!")
    return passed


def get_ndp_database(device=None) -> dict:
    return device.parse("show ndp")


def parse_cli_output(output):
    """
    Parse the NDP output into a dictionary with headers and total entries.
    """
    parsed_dict = {
        "headers": [],
        "total_entries": 0
    }

    # Split the output into lines and process
    lines = output.splitlines()

    for line in lines:
        line = line.strip()
        if "Address" in line and "MacAddress" in line:
            # Extract headers
            parsed_dict["headers"] = line.split()
        elif "Total number of entries" in line:
            # Extract total entries count
            parsed_dict["total_entries"] = int(line.split()[-1])

    return parsed_dict


def test_ndp_entries_count(parsed_data, expected_count=None) -> bool:
    try:
        actual_count = parsed_data.get("total_entries", -1)

        if actual_count != expected_count:
            raise AssertionError(
                f"Total entries count does not match. Expected: {expected_count}, Found: {actual_count}"
            )

    except Exception as e:
        print(f"Test failed due to exception: {e}")
        return False
    return True


def assert_ndp_table_headers(parsed_data, expected_headers):
    """
    Assert that the parsed table headers match the expected headers.
    """
    parsed_headers = parsed_data.get("headers", [])

    if parsed_headers != expected_headers:
        raise AssertionError(
            f"Table headers do not match. "
            f"Expected: {expected_headers}, Found: {parsed_headers}"
        )

    print("Table headers match the expected headers.")


def assert_ndp_total_entries(parsed_data, expected_count):
    """
    Assert that the total number of entries matches the expected count.
    """
    total_entries = parsed_data.get("total_entries", -1)
    if total_entries != expected_count:
        raise AssertionError(
            f"Total entries count does not match. "
            f"Expected: {expected_count}, Found: {total_entries}"
        )
    print("Total entries count matches the expected count.")


def verify_table_field_value(parsed_data, field, expected_value):
    """
    Assert that a specific field (e.g., 'status', 'mac', 'address', 'iface') matches the expected value.
    This function allows dynamic field verification and handles errors when NDP fetch fails.
    """
    # Ensure "entries" key is present in parsed_data
    if "entries" not in parsed_data:
        raise AssertionError("No 'entries' key found in parsed data. The NDP fetch may have failed.")

    # Extract entries from parsed data
    entries = parsed_data["entries"]

    # Check if entries are available and not empty
    if not entries:
        raise AssertionError("No entries found in parsed data. The NDP fetch may have failed.")

    # Iterate through all entries
    found = False
    for entry in entries:
        actual_value = entry.get(field)
        if actual_value == expected_value:
            found = True
            break

    if not found:
        raise AssertionError(f"Expected value '{expected_value}' for field '{field}' not found in any entry.")

    print(f"Field '{field}' contains the expected value: {expected_value}.")
    return True


def get_mep_database(testbed = None) -> dict:
    return testbed.parse("show oam cfm mep")


def test_if_oam_cfm_mep(testbed = None, mep_name: str = "", mep_svlan: str = "", mep_interval: int = 0) -> bool:
    try:
        mep_database = get_mep_database(testbed)
        print(mep_database)
        parsed_mep_svlan = Dq(mep_database).contains(mep_name).get_values("svlan")
        parsed_mep_interval = Dq(mep_database).contains(mep_name).get_values("interval")
        print(parsed_mep_svlan, parsed_mep_interval)
        if mep_svlan not in parsed_mep_svlan or mep_interval not in parsed_mep_interval:
            return False
    except Exception:
        return False
    return True


def get_portchannel_database(testbed=None) -> dict:
    return testbed.parse(SHOW_INTERFACES_PORTCHANNEL)


def verify_portchannel_in_output(testbed = None, channel_name: str = "") -> bool:
    try:
        port_channel_database = get_portchannel_database(testbed)
        parsed_data = Dq(port_channel_database).contains(channel_name).get_values("team_dev")
        if channel_name not in parsed_data:
            return False
    except Exception:
        return False
    return True


def get_portchannel_members(testbed = None, channel_name: str = "") -> bool:
    try:
        port_channel_database = get_portchannel_database(testbed)
        parsed_data = Dq(port_channel_database).contains(channel_name).get_values("team_dev")
        ports = []
        for interface, details in port_channel_database['sit-sm100-1']['interfaces'].items():
            if details['team_dev'] == next((channel for channel in parsed_data), None):
                ports = details['ports']
                return ports
    except Exception:
        return False


def get_portchannel_protocol(testbed = None, channel_name: str = "") -> bool:
    try:
        port_channel_database = get_portchannel_database(testbed)
        parsed_data = Dq(port_channel_database).contains(channel_name).get_values("team_dev")
        protocols = []
        for interface, details in port_channel_database['sit-sm100-1']['interfaces'].items():
            if details['team_dev'] == next((channel for channel in parsed_data), None):
                protocols = details['protocol']
                return protocols
    except Exception:
        return False


def get_radius_detail_database(testbed=None) -> dict:
    return testbed.parse(SHOW_RADIUS)


def verify_radius_global_config(testbed=None, expected_config=None) -> bool:

    radius_details = get_radius_detail_database(testbed)
    try:
        # Ensure radius_details and expected_config are provided
        if not radius_details or not expected_config:
            print("Missing radius_details or expected_config")
            return False

        # Extract the radius-global-configuration from the given details
        device_data = radius_details.get("sit-sm100-1", {}).get("radius-global-configuration", {})

        # Verify that all expected keys are present and have non-empty values
        for key, expected_value in expected_config.items():
            if key not in device_data:
                print(f"Missing key: {key}")
                return False
            if not device_data[key]:
                print(f"Key '{key}' has an empty value")
                return False

    except Exception as e:
        print(f"Error during verification: {e}")
        return False

    return True


def verify_radius_server_config(testbed=None, expected_config=None) -> bool:
    """
    Verify the radius-server configuration details.

    Args:
        testbed: The testbed object or data source containing the device details.
        expected_config: A dictionary containing the expected radius-server configuration.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """

    radius_details = get_radius_detail_database(testbed)

    try:
        # Extract actual servers data
        actual_servers = radius_details.get("sit-sm100-1", {}).get("radius-server", {}).get("servers", [])
        expected_servers = expected_config.get("servers", [])

        # Case: Both expected and actual servers are empty
        if not expected_servers and not actual_servers:
            print("Verification successful: No servers expected and none found.")
            return True

        # Case: Expected servers but none found
        if expected_servers and not actual_servers:
            print("Error: Expected the following servers but found none:")
            for server in expected_servers:
                print(f" - Address: {server['address']}, Auth-port: {server['auth-port']}, Priority: {server['priority']}")
            return False

        # Case: No servers expected but some found
        if not expected_servers and actual_servers:
            actual_server_addresses = [server.get("address") for server in actual_servers]
            print(f"Error: Expected no servers but found the following: {actual_server_addresses}.")
            return False

        # Convert lists to sets for easy comparison
        actual_set = {tuple(sorted(server.items())) for server in actual_servers}
        expected_set = {tuple(sorted(server.items())) for server in expected_servers}

        # Handle the case where actual servers exist but do not match the expected set
        if actual_set != expected_set:
            print("Mismatch found! Expected the following servers:")
            for server in expected_servers:
                print(f" - Address: {server['address']}, Auth-port: {server['auth-port']}, Priority: {server['priority']}")
            print("Found the following servers:")
            for server in actual_servers:
                print(f" - Address: {server['address']}, Auth-port: {server['auth-port']}, Priority: {server['priority']}")
            return False

    except Exception as e:
        print(f"Error during verification: {e}")
        return False

    return True


def get_mep_peer_database(testbed = None) -> dict:
    return testbed.parse("show oam cfm mep peer")


def test_if_oam_cfm_mep_peer(testbed = None, mep_name: str = "", mep_peer_id: int = 0, mep_peer_mac: str = "") -> bool:
    try:
        mep_peer_database = get_mep_peer_database(testbed)
        print(mep_peer_database)
        parsed_mep_peer_id = Dq(mep_peer_database).contains(mep_name).get_values("peer_id")
        parsed_mep_peer_mac = Dq(mep_peer_database).contains(mep_name).get_values("mac")
        print(parsed_mep_peer_id, parsed_mep_peer_mac)
        if mep_peer_id not in parsed_mep_peer_id or mep_peer_mac not in parsed_mep_peer_mac:
            return False
    except Exception:
        return False
    return True


def get_tacacs_detail_database(testbed=None) -> dict:
    return testbed.parse(SHOW_TACACS)


def verify_tacacs_global_config(testbed=None, expected_config=None) -> bool:
    """
    Verify TACACS global configuration against the expected configuration.

    Args:
        testbed: The testbed object containing device details.
        expected_config: A dictionary containing expected global TACACS configuration.

    Returns:
        bool: True if configuration matches expectations, False otherwise.
    """
    tacacs_details = get_tacacs_detail_database(testbed)

    try:
        # Ensure tacacs_details and expected_config are provided
        if not tacacs_details or not expected_config:
            print("Missing tacacs_details or expected_config")
            return False

        # Extract the TACACS global configuration for each device
        for device, tacacs_data in tacacs_details.items():
            device_data = tacacs_data.get("tacacs-global-configuration", {})

            for key, expected_value in expected_config.items():
                actual_value = device_data.get(key, "")

                # If expected value is empty, allow any value (pass if key exists)
                if expected_value == "" and key in device_data:
                    continue  # Do not fail, just ensure key exists

                # Compare expected vs actual values
                if actual_value != expected_value:
                    print(f"Mismatch on {device}: Expected {key} = {expected_value}, but found {actual_value}")
                    return False

            print(f"{device}: All expected TACACS global settings match.")
        return True

    except Exception as e:
        print(f"Error during verification: {e}")
        return False


def set_default_tacacs_config(testbed = None) -> None:
    tacacs_commands = [
        SonicCommands.AUTH_TYPE.value,
        SonicCommands.PASSKEY.value,
        SonicCommands.TIMEOUT.value
    ]
    try:
        for command in tacacs_commands:
            testbed.execute(f"sudo {SonicCommands.CONFIG_TACACS.value} {SonicCommands.DEFAULT.value} {command}")
    except Exception as e:
        log.debug(f"{e}")
    else:
        log.debug("TACACS configuration has been set to default values")


def set_interface_naming_mode(testbed = None, naming_mode: str = "default") -> None:
    try:
        testbed.execute(f"sudo {SonicCommands.CONFIG_INTERFACE_NAMING_MODE.value} {naming_mode}")
        testbed.execute(SonicCommands.SHOW_VLAN_CONFIG.value)
    except Exception as e:
        log.debug(f"{e}")
    else:
        log.debug(f"Interface Naming Mode has been set to '{naming_mode}'")


def set_default_radius_config(testbed = None) -> None:
    radius_commands = [
        SonicCommands.AUTH_TYPE.value,
        SonicCommands.RETRANSMIT.value,
        SonicCommands.TIMEOUT.value,
        SonicCommands.PASSKEY.value
    ]
    try:
        for command in radius_commands:
            testbed.execute(f"sudo {SonicCommands.CONFIG_RADIUS.value} {SonicCommands.DEFAULT.value} {command}")
    except Exception as e:
        log.debug(f"{e}")
    else:
        log.debug("RADIUS configuration has been set to default values")


def cleanup_authentication_servers(testbed, server_type):
    """
    Removes all configured authentication servers (TACACS or RADIUS) from the device.

    Args:
        testbed: The testbed object for executing commands on the device.
        server_type (str): Type of server to clean up ("TACACS" or "RADIUS").
    """
    if server_type.upper() == "TACACS":
        show_command = SHOW_TACACS
        config_command = SonicCommands.CONFIG_TACACS
        identifier = "TACPLUS_SERVER"
    elif server_type.upper() == "RADIUS":
        show_command = SHOW_RADIUS
        config_command = SonicCommands.CONFIG_RADIUS
        identifier = "RADIUS_SERVER"
    else:
        log.error(f"Invalid server type: {server_type}. Use 'TACACS' or 'RADIUS'.")
        return

    log.info(f"Fetching configured {server_type} servers before cleanup...")

    try:
        output = testbed.execute(show_command)
        log.info(f"Command output: {output}")

        device_data = output.get('sit-sm100-1', '')
        servers = []
        lines = device_data.splitlines()

        for line in lines:
            if identifier in line:
                parts = line.split()
                if len(parts) >= 3:
                    server_address = parts[2]
                    servers.append(server_address)

        # Check if any servers are found
        if not servers:
            log.info(f"No {server_type} servers found. Skipping cleanup.")
            return

        # Delete all configured servers
        for server in servers:
            log.info(f"Removing {server_type} server: {server}")
            testbed.execute(f"sudo {config_command.with_args(SonicCommands.DELETE.value, server)}")

        log.info(f"Successfully removed all configured {server_type} servers.")

    except Exception as e:
        log.error(f"Failed to remove {server_type} servers: {e}")
        raise RuntimeError(f"{server_type} cleanup failed: {e}")


def set_default_aaa_config(testbed = None) -> None:
    default_aaa_commands = [
        (SonicCommands.AUTHENTICATION.value, SonicCommands.LOGIN.value, SonicCommands.LOCAL.value),
        (SonicCommands.AUTHENTICATION.value, SonicCommands.FAILTHROUGH.value, SonicCommands.DEFAULT.value),
        (SonicCommands.AUTHENTICATION.value, SonicCommands.DEBUG.value, SonicCommands.DEFAULT.value),
        (SonicCommands.AUTHENTICATION.value, SonicCommands.FALLBACK.value, SonicCommands.DEFAULT.value),
        (SonicCommands.AUTHENTICATION.value, SonicCommands.TRACE.value, SonicCommands.DEFAULT.value),
        (SonicCommands.AUTHORIZATION.value, SonicCommands.LOCAL.value, None),
        (SonicCommands.ACCOUNTING.value, SonicCommands.DISABLE.value, None),
    ]

    try:
        for section, command, value in default_aaa_commands:
            # Construct and execute the command
            if value is not None:
                cmd_str = f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_AAA.value} {section} {command} {value}"
            else:
                cmd_str = f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_AAA.value} {section} {command}"

            testbed.execute(cmd_str)

    except Exception as e:
        log.debug(f"Failed to set AAA configuration: {e}")
    else:
        log.debug("AAA configuration has been set to default values")


def get_aaa_details(testbed=None) -> dict:
    """Retrieve the AAA configuration details from the device."""
    return testbed.parse(SHOW_AAA)


def verify_aaa_config(testbed=None, expected_config=None) -> bool:
    """Verify AAA configuration methods for authentication, authorization, and accounting.

    Args:
        testbed: The testbed instance for executing commands.
        expected_config: A dictionary with expected values for 'authentication',
                          'authorization', and 'accounting'.

    Returns:
        bool: True if all expected values match the actual configuration; False otherwise.
    """
    aaa_details = get_aaa_details(testbed)
    
    if not aaa_details:
        print("Missing aaa_details")
        return False

    device_data = aaa_details.get("sit-sm100-1", {}).get("aaa", {})

    # Verify each expected configuration
    for section, expected in expected_config.items():
        actual = device_data.get(section, {})
        
        # Check if the expected value matches the actual value
        for key, expected_value in expected.items():
            actual_value = actual.get(key, "")
            if expected_value and actual_value != expected_value:
                print(f"Expected {section} {key} '{expected_value}' but found '{actual_value}'")
                return False

    return True


def verify_tacacs_server_config(testbed, expected_config, key_to_validate=None):
    """
    Verify the TACACS server configuration details per server.

    Args:
        testbed: The testbed object containing the device details.
        expected_config: A dictionary mapping server addresses to expected configurations.
        key_to_validate: (Optional) Specific key to validate within the TACACS server configuration.

    Returns:
        bool: True if all checked servers match expectations, False if any mismatch is found.
    """
    try:
        # Get TACACS details from the testbed
        tacacs_details = get_tacacs_detail_database(testbed)

        for device, tacacs_data in tacacs_details.items():
            print(f"\nVerifying TACACS server configuration for device: {device}")

            # Extract TACACS server configuration
            server_config_list = tacacs_data.get("tacacs-server", {}).get("servers", [])

            if not server_config_list:
                print(f"No TACACS servers configured on {device}.")
                return False

            for server in server_config_list:
                server_address = server.get("address", "Unknown")

                # Check if the server has the expected values
                if server_address in expected_config:
                    expected_value = expected_config[server_address].get(key_to_validate)
                    actual_value = server.get(key_to_validate)

                    if actual_value != expected_value:
                        print(f"Mismatch on {device} - TACACS Server {server_address}: "
                              f"Expected {key_to_validate} = {expected_value}, but found {actual_value}")
                        return False
                    else:
                        print(f"TACACS Server {server_address}: {key_to_validate} matches {expected_value}")

                else:
                    print(f"Unexpected TACACS server {server_address} found on {device}. Continuing verification...")

        return True

    except Exception as e:
        print(f"Error during verification: {e}")
        return False


def cleanup_portchannels(testbed):
    """
    Cleanup method to delete all created port channels and their members.
    """
    try:
        port_channel_database = get_portchannel_database(testbed)
        interfaces = port_channel_database.get("sit-sm100-1", {}).get("interfaces", {})

        # Extract PortChannels and their members
        portchannels = {
            details.get("team_dev"): details.get("ports", [])
            for details in interfaces.values()
            if "PortChannel" in details.get("team_dev", "")
        }

        if not portchannels:
            log.info("No PortChannels found. Skipping Cleanup...")
            return

        # First, remove members from each PortChannel
        for portchannel, members in portchannels.items():
            for member in members:
                member = member.split("(")[0]
                testbed.execute(
                    f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_PORTCHANNEL.with_args(SonicCommands.MEMBER.value, SonicCommands.DEL.value, portchannel, member)}"
                )
                log.info(f"Removed {member} from {portchannel}")

        # Delete each PortChannel
        for portchannel in portchannels.keys():
            testbed.execute(
                f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_PORTCHANNEL.with_args(SonicCommands.DEL.value, portchannel)}"
            )
            log.info(f"Deleted {portchannel}")

        log.info("PortChannel cleanup completed successfully.")

    except Exception as e:
        log.error(f"Error during cleanup: {str(e)}")


def verify_portchannel_members(testbed=None, channel_name: str = "") -> list:
    try:
        device = testbed.devices["sit-sm100-1"]

        # Get PortChannel members
        interfaces = get_portchannel_database(testbed).get("sit-sm100-1", {}).get("interfaces", {})
        port_members = [
            port.split("(")[0] for details in interfaces.values()
            if details.get("team_dev") == channel_name
            for port in details.get("ports", [])
        ]

        # Get interface alias mappings
        interface_status = device.parse(f"{SonicCommands.SHOW.value} {SonicCommands.INTERFACES.value} {SonicCommands.STATUS.value}")
        alias_mapping = {
            details["alias"]: interface for interface, details in interface_status.get("interfaces", {}).items()
        }

        # Normalize members: Replace alias with interface name if needed
        normalized_members = {alias_mapping.get(port, port) for port in port_members}

        return list(normalized_members)

    except Exception as e:
        print(f"Error in verify_portchannel_members: {e}")
        return []


def create_portchannel(testbed, portchannel_name):
    """Creates a PortChannel and verifies it is successfully created."""
    try:
        testbed.execute(
            f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_PORTCHANNEL.with_args(SonicCommands.ADD.value, portchannel_name)}"
        )

        if not verify_portchannel_in_output(testbed, portchannel_name):
            raise Exception(f"Could not find {portchannel_name}")

        print(f"Successfully created PortChannel {portchannel_name}")

    except Exception as e:
        print(f"Error creating PortChannel {portchannel_name}: {e}")
        raise


def add_member_to_portchannel(testbed, portchannel_name, member_interface):
    """Adds an interface to a PortChannel."""
    try:
        testbed.execute(
            f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_PORTCHANNEL.with_args(SonicCommands.MEMBER.value, SonicCommands.ADD.value, portchannel_name, member_interface)}"
        )

        port_members = verify_portchannel_members(testbed, portchannel_name)

        if member_interface not in port_members:
            raise Exception(f"{member_interface} was not found as a member of {portchannel_name}")

        print(f"Successfully added {member_interface} to {portchannel_name}")

    except Exception as e:
        print(f"Error adding {member_interface} to {portchannel_name}: {e}")
        raise


def verify_portchannel_status(testbed, portchannel_name):
    """
    Verifies the status of a given PortChannel in SONiC.

    Args:
        testbed: The pyATS testbed object for device interaction.
        portchannel_name (str): The name of the PortChannel to check.

    Returns:
        str: The status of the PortChannel
    """
    portchannel_data = get_portchannel_database(testbed)

    # Extract device-specific data (assuming single device for now)
    device_name = next(iter(portchannel_data.keys()))
    interfaces_data = portchannel_data[device_name].get("interfaces", {})

    # Search for the given PortChannel name
    for key, values in interfaces_data.items():
        if values.get("team_dev") == portchannel_name:
            return values.get("protocol", "unknown")

    raise Exception(f"PortChannel {portchannel_name} not found in the output")


def execute_command(testbed, action, interfaces):
    """Helper function to execute interface commands."""
    for intf in interfaces:
        testbed.execute(
            f"{SonicCommands.SUDO.value} {SonicCommands.CONFIG_INTERFACE.with_args(action, intf)}"
        )


def get_expected_error_message(error_type, **kwargs):
    """
    Returns the expected error message based on the error type.

    :param error_type: Type of the error message to fetch.
    :param kwargs: Dictionary containing required values for formatting.
    :return: Formatted error message.
    """
    error_messages = {
        "invalid_interface_name": "Error: Interface name {interface} is invalid. Please enter a valid interface name!!",
        "lag_member_ip_assign": "Error: {interface} is configured as a member of portchannel.",
        "invalid_portchannel_name": "Error: {portchannel_name} is invalid!, name should have prefix 'PortChannel' and suffix '<1-64>'",
        "lag_member_multiple_portchannel": "Error: {interface} Interface is already member of {portchannel_name}",
        "max_member_count": "Error:  {portchannel_name} has {max_members} members. Maximum member count  reached.",
        "name_conflict": "Error: {portchannel_name} already exists!",
        "not_a_member_error": "Error: {interface} is not a member of portchannel {portchannel_name}",
        "port_speed_error": "Error: Port speed of {interface} is different than the other members of the portchannel {portchannel_name}",
        "vlan_member_error": "Error: {interface} Interface configured as VLAN_MEMBER under vlan : {vlan_value}",
        "portchannel_member_error": "Error: {interface} is part of portchannel!",
    }

    if error_type in error_messages:
        return error_messages[error_type].format(**kwargs)
    else:
        raise ValueError(f"Unknown error type: {error_type}")


def generate_invalid_portchannels():
    return [
        f"PortChannel_{i}" for i in range(101, 103)
    ] + [
        f"Port-Channel{i}" for i in range(1, 3)
    ] + [
        "ChannelX",
        "PortChannel0",
        "PortChannel65"
    ]


def add_multiple_members_to_portchannel(testbed, portchannel_name, start_range, end_range):
    """
    Dynamically adds specified Ethernet interfaces to a specified PortChannel.

    Args:
        testbed: The testbed object to execute commands on.
        portchannel_name: The name of the PortChannel to which interfaces will be added.
        start_range: The starting number of the Ethernet interfaces.
        end_range: The ending number of the Ethernet interfaces.

    Raises:
        Exception: If adding any member to the PortChannel fails.
    """
    existing_members = [f"Ethernet{i}" for i in range(start_range, end_range + 1)]  # Create member interfaces from the specified range
    for member in existing_members:
        try:
            add_member_to_portchannel(testbed, portchannel_name, member)
        except Exception as e:
            raise Exception(f"Failed to add {member} to {portchannel_name}: {e}") from e


def verify_expected_error(raw_data, expected_error_message):
    """
    Verifies that the expected error message appears in the provided command output.

    Args:
        command_output (str): The raw command output to check for errors.
        expected_error_message (str): The expected error message.

    Raises:
        Exception: If the expected error message is not found.
    """
    output = raw_data.get("sit-sm100-1", "").strip()
    actual_error_message = next((line.strip() for line in output.split("\n") if line.startswith("Error:")), "")

    if actual_error_message == expected_error_message:
        log.info(f"Expected failure: {expected_error_message}")
    else:
        error_msg = (
            f"Unexpected success: Expected error message was not found.\n"
            f"Expected: {expected_error_message}\n"
            f"Actual: {actual_error_message or 'No error message found'}"
        )
        log.error(error_msg)
        raise Exception(error_msg)


def verify_interface_field(testbed, interface_name, field_name, expected_values):
    """
    Verifies if the specified field of an interface contains expected values.

    Args:
        testbed: The testbed object.
        interface_name (str): The name of the interface to check.
        field_name (str): The field to verify (e.g., "vlan").
        expected_values (list): A list of expected values (e.g., ["trunk", "PortChannel01"]).

    Returns:
        bool: True if the field contains an expected value, False otherwise.

    Raises:
        Exception: If the field does not contain the expected value.
    """
    raw_output_dict = testbed.execute(
        f"{SonicCommands.SHOW.value} {SonicCommands.INTERFACES.value} {SonicCommands.STATUS.value} {interface_name}"
    )

    raw_output = raw_output_dict.get("sit-sm100-1", "").strip()

    if not raw_output:
        raise Exception(f"No output received for interface {interface_name}")

    # Regex pattern to extract relevant fields
    pattern = rf"{interface_name}\s+\S+\s+\S+\s+\d+\s+\S+\s+\S+\s+(?P<vlan>\S+)\s+(?P<oper>\S+)\s+(?P<admin>\S+)\s+(?P<type>\S+)\s+(?P<asym_pfc>\S+)"

    match = re.search(pattern, raw_output)
    if not match:
        raise Exception(f"Failed to parse interface status for {interface_name}")

    # Extract the required field value
    field_value = match.groupdict().get(field_name.lower())

    if field_value is None:
        raise Exception(f"Field '{field_name}' not found for interface {interface_name}")

    if field_value in expected_values:
        return True

    raise Exception(f"{interface_name} - {field_name} is '{field_value}', expected {expected_values}")


def verify_portchannel_headers(testbed=None) -> bool:
    """
    Verifies the presence of required headers in the parsed output.
    """
    try:
        parsed_data = get_portchannel_database(testbed)

        # Extract the first available device (e.g., 'sit-sm100-1')
        device_data = next(iter(parsed_data.values()), {})
        first_interface = next(iter(device_data.get("interfaces", {}).values()), None)

        if not first_interface:
            print("Error: No interface data found.")
            return False

        # Required headers based on the parser schema
        required_headers = {"team_dev", "protocol", "ports"}

        if not required_headers.issubset(first_interface.keys()):
            print(f"Missing headers: {required_headers - set(first_interface.keys())}")
            return False

        return True
    except Exception as e:
        print(f"Failed to verify headers: {e}")
        return False


def get_portchannel_flags(testbed, device_name="sit-sm100-1"):
    """
    Extracts and returns the set of flags from the 'show interfaces portchannel' output.
    """
    try:
        # Execute command and get raw output (dictionary format)
        raw_output = testbed.execute(SHOW_INTERFACES_PORTCHANNEL)
        log.info(f"Command output:\n{raw_output}")

        # Extract output string from the dictionary using the device name
        output_str = raw_output.get(device_name, "")
        if not output_str:
            log.error(f"No output found for device {device_name}.")
            return set()

        # Extract Flags line using regex
        match = re.search(r"Flags:\s*(.+)", output_str)
        if not match:
            log.error("Flags information not found in the command output.")
            return set()

        # Extract flags and convert to a set (handles both commas and spaces)
        return set(re.split(r"[, ]+", match.group(1).strip()))

    except Exception as e:
        log.error(f"Failed to retrieve flags: {e}")
        return set()


def clean_table_output(raw_output: str):
    """
    Cleans the raw output by removing table formatting characters and extracting only relevant data.
    
    :param raw_output: Raw string output from the VLAN table.
    :return: List of cleaned lines containing meaningful VLAN data.
    """
    # Remove lines that contain only dashes, plus signs, and equal signs
    cleaned_lines = [
        line for line in raw_output.splitlines()
        if not re.match(r"^[\s\-\+=|]+$", line)
    ]
    return cleaned_lines


def parse_vlan_data(raw_output: dict):
    """
    Parses VLAN data from raw device output and ensures correct IP Address and port-tagging assignments.
    
    :param raw_output: Dictionary containing the device output with VLAN information.
    :return: Parsed VLAN dictionary with structured data.
    """
    parsed_data = {}

    for device, output in raw_output.items():
        cleaned_lines = clean_table_output(output)
        vlan_list = []
        vlan_entry = None

        for line in cleaned_lines:
            columns = line.split("|")
            columns = [col.strip() for col in columns if col.strip()]

            if not columns:
                continue

            # New VLAN entry found
            if columns[0].startswith("Vlan"):
                if vlan_entry:
                    vlan_list.append(vlan_entry)

                vlan_entry = {
                    "VLAN": columns[0],
                    "IP Address": columns[1] if len(columns) > 1 and columns[1] else None,
                    "Ports": {},  # Store ports as key-value pairs {port: tagging}
                    "Proxy ARP": columns[4] if len(columns) > 4 else None,
                    "Terminate": columns[5] if len(columns) > 5 else None
                }

                # If the VLAN has a port entry, capture it
                if len(columns) > 2 and columns[2]:
                    vlan_entry["Ports"][columns[2]] = columns[3]

            # Handling additional ports under the same VLAN
            elif vlan_entry and len(columns) >= 3 and columns[2]:
                vlan_entry["Ports"][columns[2]] = columns[3]

        if vlan_entry:
            vlan_list.append(vlan_entry)

        parsed_data[device] = vlan_list

    return parsed_data


def verify_vlan(parsed_output: dict, vlan_id: str, expected_ip: str, expected_ports: dict):
    """
    Verifies if a VLAN exists in the parsed output with expected IP Address and port-tagging.
    If tagging is missing, it raises an assertion failure.

    :param parsed_output: Dictionary containing parsed VLAN data.
    :param vlan_id: VLAN to verify.
    :param expected_ip: Expected IP Address for the VLAN.
    :param expected_ports: Expected ports and their tagging (e.g., {"PortChannel11": "tagged"}).
    :return: None. Raises an exception if validation fails.
    """
    print(f"DEBUG: Verifying VLAN {vlan_id} in parsed output...")

    try:
        for device, vlan_list in parsed_output.items():
            if not isinstance(vlan_list, list):
                raise Exception(f"VLAN data is not in expected format for device {device}")

            vlan_entry = next((v for v in vlan_list if v["VLAN"] == vlan_id), None)
            if not vlan_entry:
                raise Exception(f"VLAN {vlan_id} not found. Available VLANs: {[v['VLAN'] for v in vlan_list]}")

            # Verify IP Address
            actual_ip = vlan_entry.get("IP Address")
            if actual_ip != expected_ip:
                raise Exception(f"VLAN {vlan_id} has incorrect IP Address. Expected: {expected_ip}, Found: {actual_ip}")

            # Extract ports dictionary from parsed data
            vlan_ports_dict = vlan_entry.get("Ports", {})
            if not vlan_ports_dict:
                raise Exception(f"VLAN {vlan_id} has no ports assigned.")

            # Check each expected port
            for port, expected_tagging in expected_ports.items():
                if expected_tagging not in vlan_ports_dict:
                    raise Exception(f"CRITICAL FAIL: Expected tagging '{expected_tagging}' is missing in VLAN {vlan_id}. "
                                     f"Available tags: {list(vlan_ports_dict.keys())}")
                
                # Verify port name matches expected IP Address
                if actual_ip != port:
                    raise Exception(f"FAIL: VLAN {vlan_id} IP Address mismatch. Expected IP '{port}', but found '{actual_ip}'.")

        print(f"PASS: VLAN {vlan_id} found with correct IP Address and expected port tagging.")

    except Exception as e:
        print(f"FAIL: {e}")
        raise


if __name__ == "__main__":
    # qinq to trunk
    parsed = {'sit-sm100-1': {'vlans': {'S-Vlan200': {'admin': 'up',
                                         'aging': 300,
                                         'mac_learn': 'enabled',
                                         'mac_limit': 64,
                                         'ports': {'Ethernet26': {'port_tagging': 'double_tagged'},
                                                   'Vlan100': {'port_tagging': 'tagged'}},
                                         'vid': 200},
                           'Vlan1': {'admin': 'down',
                                     'aging': 300,
                                     'mac_learn': 'enabled',
                                     'mac_limit': 64,
                                     'ports': {'Ethernet16': {'port_tagging': 'untagged'},
                                               'Ethernet17': {'port_tagging': 'untagged'},
                                               'Ethernet18': {'port_tagging': 'untagged'},
                                               'Ethernet19': {'port_tagging': 'untagged'},
                                               'Ethernet20': {'port_tagging': 'untagged'},
                                               'Ethernet21': {'port_tagging': 'untagged'},
                                               'Ethernet22': {'port_tagging': 'untagged'},
                                               'Ethernet23': {'port_tagging': 'untagged'},
                                               'Ethernet24': {'port_tagging': 'untagged'},
                                               'Ethernet25': {'port_tagging': 'untagged'},
                                               'Ethernet26': {'port_tagging': 'untagged'},
                                               'Ethernet27': {'port_tagging': 'untagged'},
                                               'Ethernet28': {'port_tagging': 'untagged'},
                                               'Ethernet29': {'port_tagging': 'untagged'},
                                               'Ethernet30': {'port_tagging': 'untagged'},
                                               'Ethernet31': {'port_tagging': 'untagged'}},
                                     'vid': 1},
                           'Vlan100': {'admin': 'up',
                                       'aging': 300,
                                       'mac_learn': 'enabled',
                                       'mac_limit': 64,
                                       'ports': {'Ethernet16': {'port_tagging': 'tagged'}},
                                       'vid': 100}}}}
