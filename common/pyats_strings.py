from enum import Enum, auto


class Weekdays(Enum):
    Mon = 0
    Tue = auto()
    Wed = auto()
    Thu = auto()
    Fri = auto()
    Sat = auto()
    Sun = auto()


class Months(Enum):
    Jan = 1
    Feb = auto()
    Mar = auto()
    Apr = auto()
    May = auto()
    Jun = auto()
    Jul = auto()
    Aug = auto()
    Sep = auto()
    Oct = auto()
    Nov = auto()
    Dec = auto()


WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TIME_ZONES = [
    "ACDT",
    "ACST",
    "ACT",
    "ACT",
    "ACWST",
    "ADT",
    "AEDT",
    "AEST",
    "AET (AEST/AEDT)",
    "AFT",
    "AKDT",
    "AKST",
    "ALMT",
    "AMST",
    "AMT",
    "AMT",
    "ANAT",
    "AQTT",
    "ART",
    "AST",
    "AST",
    "AWST",
    "AZOST",
    "AZOT",
    "AZT",
    "BNT",
    "BIOT",
    "BIT",
    "BOT",
    "BRST",
    "BRT",
    "BST",
    "BST",
    "BST",
    "BTT",
    "CAT",
    "CCT",
    "CDT",
    "CDT",
    "CEST",
    "CET",
    "CHADT",
    "CHAST",
    "CHOT",
    "CHOST",
    "CHST",
    "CHUT",
    "CIST",
    "CKT",
    "CLST",
    "CLT",
    "COST",
    "COT",
    "CST",
    "CST",
    "CST",
    "CT (CST/CDT)",
    "CVT",
    "CWST",
    "CXT",
    "DAVT",
    "DDUT",
    "DFT",
    "EASST",
    "EAST",
    "EAT",
    "ECT",
    "ECT",
    "EDT",
    "EEST",
    "EET",
    "EGST",
    "EGT",
    "EST",
    "ET (EST/EDT)",
    "FET",
    "FJT",
    "FKST",
    "FKT",
    "FNT",
    "GALT",
    "GAMT",
    "GET",
    "GFT",
    "GILT",
    "GIT",
    "GMT",
    "GST",
    "GST",
    "GYT",
    "HDT",
    "HAEC",
    "HST",
    "HKT",
    "HMT",
    "HOVST",
    "HOVT",
    "ICT",
    "IDLW",
    "IDT",
    "IOT",
    "IRDT",
    "IRKT",
    "IRST",
    "IST",
    "IST",
    "IST",
    "JST",
    "KALT",
    "KGT",
    "KOST",
    "KRAT",
    "KST",
    "LHST",
    "LHST",
    "LINT",
    "MAGT",
    "MART",
    "MAWT",
    "MDT",
    "MET",
    "MEST",
    "MHT",
    "MIST",
    "MIT",
    "MMT",
    "MSK",
    "MST",
    "MST",
    "MT (MST/MDT)",
    "MUT",
    "MVT",
    "MYT",
    "NCT",
    "NDT",
    "NFT",
    "NOVT",
    "NPT",
    "NST",
    "NT",
    "NUT",
    "NZDT",
    "NZST",
    "OMST",
    "ORAT",
    "PDT",
    "PET",
    "PETT",
    "PGT",
    "PHOT",
    "PHT",
    "PHST",
    "PKT",
    "PMDT",
    "PMST",
    "PONT",
    "PST",
    "PT (PST/PDT)",
    "PWT",
    "PYST",
    "PYT",
    "RET",
    "ROTT",
    "SAKT",
    "SAMT",
    "SAST",
    "SBT",
    "SCT",
    "SDT",
    "SGT",
    "SLST",
    "SRET",
    "SRT",
    "SST",
    "SST",
    "SYOT",
    "TAHT",
    "THA",
    "TFT",
    "TJT",
    "TKT",
    "TLT",
    "TMT",
    "TRT",
    "TOT",
    "TST",
    "TVT",
    "ULAST",
    "ULAT",
    "UTC",
    "UYST",
    "UYT",
    "UZT",
    "VET",
    "VLAT",
    "VOLT",
    "VOST",
    "VUT",
    "WAKT",
    "WAST",
    "WAT",
    "WEST",
    "WET",
    "WIB",
    "WIT",
    "WITA",
    "WGST",
    "WGT",
    "WST",
    "YAKT",
    "YEKT"
]


class TacacsConfig(Enum):
    INVALID_SERVER = "192.168.1.256"
    PRIMARY_SERVER = "11.11.11.11"
    SECONDARY_SERVER = "11.11.11.12"
    SHARED_SECRET_1 = "testing123"
    SHARED_SECRET_2 = "testing456"
    WRONG_KEY = "wrongkey"
    TIMEOUT_1 = "15"
    TIMEOUT_2 = "50"
    PRIORITY_1 = '1'
    PRIORITY_2 = '2'
    CUSTOM_PORT = '49'
    INVALID_PORT = '65536'
    IPv6_ADDRESS = "fd00:c0a8:a54:2222::1"
    INVALID_TACACS_USER = "test_invalid_user"
    INVALID_TACACS_PASSWORD = "test123456"
    AUTH_TYPE_CHAP = "chap"
    TCP_PORT_1 = "149"
    TCP_PORT_2 = "14941"


class RadiusConfig(Enum):
    RADIUS_SERVER_TITLE = "RADIUS_SERVER"
    PRIMARY_SERVER = "192.168.1.10"
    SECONDARY_SERVER = "192.168.1.11"
    SHARED_SECRET_1 = "testing123"
    SHARED_SECRET_2 = "testing456"
    DEFAULT_AUTH_PORT = "1812"
    TIMEOUT_1 = "10"
    RETRANSMIT_COUNT = "4"
    IP_ADDRESS = "192.168.1.5"
    CUSTOM_AUTH_PORT = "1822"
    PRIORITY_1 = '1'
    PRIORITY_2 = '2'
    NON_DEFAULT_AUTH_PORT = "10"


class PortChannelConfig(Enum):
    PORTCHANNEL_NAME_1 = "PortChannel11"
    PORTCHANNEL_NAME_2 = "PortChannel12"
    IP_ADDRESS = "10.16.9.150"
    INVALID_PORT_ETH_50 = "Ethernet50"
    DEFAULT_VLAN_STATUS = "trunk"
    DEFAULT_PROTOCOL_STATUS = "LACP(A)(Dw)"
    VLAN_INT = "2"
