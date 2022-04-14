RELEASE = True
APP_NAME = "Marsnake"
VERSION = "1.6.1"

#MACRO
FILE_TRANSFER_SIZE_PER_TIME = 1 * 1024 * 1024
SOCKET_BUFFER_SIZE = 10 * 1024 * 1024
SOCKET_RECV_SIZE = 1 * 1024 * 1024
MALWARE_FILE_MAX_SIZE = 10 * 1024 * 1024

#SECURITY AUDIT
AUDIT_SCAN_PERIOD = 5 * 60

#RSA KEYS
SERVER_PUBLIC_KEY = "config/server_public_key.pem"

#CONFIG
CLEANER_CONF = "config/cleaner"
LANGUAGE_CONF = "config/language"
PCIDB_CONF = "config/pci.ids"

#LOG
LOG_DIR = "logs"
LOG_NAME = "marsnake.log"
LOG_MAX_BYTES = 20 * 1024 * 1024
LOG_BACKUP_COUNT = 1

#DB
DB_DIR = "db"
DB_MONITOR = "monitor.pkl"
DB_BASIC = "basic.pkl"
DB_BASELINE = "baseline.pkl"
DB_FINGERPRINT = "fingerprint.pkl"
DB_VULS = "vuls.pkl"
DB_UEBA = "ueba.pkl"
DB_AUDIT = "audit.pkl"
DB_SETTING = "setting.pkl"
DB_STRATEGY = "strategy.pkl"
DB_VIRUS = "virus.pkl"
DB_VIRUS_WHITELIST = "whitelist.pkl"

#ISOLATION
ISOLATION_PATH = "isolation"

if RELEASE:
	SERVER_URL = "marsnake.com:443"
else:
	SERVER_URL = "10.16.60.202:8080"
