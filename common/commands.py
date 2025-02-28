
from enum import Enum


SHOW_ARP = "show arp"

SHOW_AAA = "show aaa"

SHOW_TACACS = "show tacacs"

SHOW_VERSION = "show version"

SHOW_CLOCK = "show clock"
DATE_ERROR = "does not conform format YYYY-MM-DD"
TIME_ERROR = "does not conform format HH:MM:SS"

SHOW_REBOOT_CAUSE = "show reboot-cause"
SHOW_REBOOT_CAUSE_HISTORY = "show reboot-cause history"

SHOW_SUPPRESS_FIB_PENDING = "show suppress-fib-pending"

SHOW_LINE = "show line"

SHOW_AT_GLOBAL = "show auto-techsupport global"
SHOW_AT_HISTORY = "show auto-techsupport history"
SHOW_AT_FEATURE = "show auto-techsupport-feature"

SHOW_FEATURE_AUTORESTART = "show feature autorestart"
SHOW_FEATURE_CONFIG = "show feature config"
SHOW_FEATURE_STATUS = "show feature status"

CONFIG_PORTCHANNEL_ADD = "config portchannel add"
SHOW_INTERFACES_PORTCHANNEL = "show interfaces portchannel"
CONFIG_PORTCHANNEL_DELETE = "config portchannel del"
CONFIG_PORTCHANNEL_MEMBER_ADD = "config portchannel member add"

SHOW_RADIUS = "show radius"

SHOW_STP = "show spanning-tree"
CONFIG_STP = "config spanning-tree"


class SonicCommands(Enum):
    CONFIG_AAA = "config aaa"
    CONFIG_TACACS = "config tacacs"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ACCOUNTING = "accounting"
    LOGIN = "login"
    DEFAULT = "default"
    FALLBACK = "fallback"
    TACACS = "tacacs+"
    LOCAL = "local"
    ENABLE = "enable"
    TIMEOUT = "timeout"
    DELETE = "delete"
    PASSKEY = "passkey"
    DISABLE = "disable"
    RADIUS = "radius"
    CONFIG_INTERFACE_NAMING_MODE = "config interface_naming_mode"
    SHOW_VLAN_CONFIG = "show vlan config"
    CONFIG_PORTCHANNEL_MEMBER_DELETE = "config portchannel member del"
    CONFIG_RADIUS = "config radius"
    SOURCE_IP = "sourceip"
    AUTH_TYPE = "authtype"
    FAILTHROUGH = "failthrough"
    DEBUG = "debug"
    TRACE = "trace"
    RETRANSMIT = "retransmit"
    SUDO = "sudo"
    ADD = "add"
    CONFIG_PORTCHANNEL = "config portchannel"
    DEL = "del"
    MEMBER = "member"
    SHOW = "show"
    INTERFACES = "interfaces"
    STATUS = "status"
    CONFIG_INTERFACE = "config interface"
    SHUTDOWN = "shutdown"
    STARTUP = "startup"
    IP = "ip"
    SPEED = "speed"
    CONFIG_VLAN = "config vlan"
    SHOW_VLAN_BRIEF = "show vlan brief"

    def with_args(self, *args):
        """
        Dynamically append arguments to the base command.

        Args:
            *args: Additional arguments to append to the command.

        Returns:
            str: The complete command with appended arguments.
        """
        return f"{self.value} {' '.join(args)}"
