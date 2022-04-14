RELEASE = True
APP_NAME = &#34;Marsnake&#34;
VERSION = &#34;1.6.1&#34;

#MACRO
FILE_TRANSFER_SIZE_PER_TIME = 1 * 1024 * 1024
SOCKET_BUFFER_SIZE = 10 * 1024 * 1024
SOCKET_RECV_SIZE = 1 * 1024 * 1024
MALWARE_FILE_MAX_SIZE = 10 * 1024 * 1024

#SECURITY AUDIT
AUDIT_SCAN_PERIOD = 5 * 60

#RSA KEYS
SERVER_PUBLIC_KEY = &#34;config/server_public_key.pem&#34;

#CONFIG
CLEANER_CONF = &#34;config/cleaner&#34;
LANGUAGE_CONF = &#34;config/language&#34;
PCIDB_CONF = &#34;config/pci.ids&#34;

#LOG
LOG_DIR = &#34;logs&#34;
LOG_NAME = &#34;marsnake.log&#34;
LOG_MAX_BYTES = 20 * 1024 * 1024
LOG_BACKUP_COUNT = 1

#DB
DB_DIR = &#34;db&#34;
DB_MONITOR = &#34;monitor.pkl&#34;
DB_BASIC = &#34;basic.pkl&#34;
DB_BASELINE = &#34;baseline.pkl&#34;
DB_FINGERPRINT = &#34;fingerprint.pkl&#34;
DB_VULS = &#34;vuls.pkl&#34;
DB_UEBA = &#34;ueba.pkl&#34;
DB_AUDIT = &#34;audit.pkl&#34;
DB_SETTING = &#34;setting.pkl&#34;
DB_STRATEGY = &#34;strategy.pkl&#34;
DB_VIRUS = &#34;virus.pkl&#34;
DB_VIRUS_WHITELIST = &#34;whitelist.pkl&#34;

#ISOLATION
ISOLATION_PATH = &#34;isolation&#34;

if RELEASE:
	SERVER_URL = &#34;marsnake.com:443&#34;
else:
	SERVER_URL = &#34;10.16.60.202:8080&#34;
