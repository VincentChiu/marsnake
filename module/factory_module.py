from utils.singleton import singleton
from concurrent.futures import ThreadPoolExecutor
from utils import common, import_helper
from core.logger import Klogger
from core.threads import Kthreads
import sys, imp
import threading

def load_mod(mod_path):
	mod_path = mod_path.replace(&#34;/&#34;, &#34;.&#34;).rsplit(&#34;.&#34;, 1)[0]
	mod = None

	try:
		mod = import_helper.import_module(mod_path)
	except Exception as e:
		Klogger().exception()

	return mod

def run_mod(mod_run, payload, socket):
	try:
		#Kthreads().set_name(&#34;module-{}&#34;.format(mod_run.__module__))
		mod_run.run(payload, socket)
	except Exception as e:
		Klogger().exception()

@singleton
class Kmodules():
	def __init__(self):
		pass

	def on_initializing(self, *args, **kwargs):
		self.modules = {
			&#34;0&#34; : load_mod(&#34;module/basic/heartbeat.py&#34;),
			&#34;1&#34; : load_mod(&#34;module/basic/remote_verification.py&#34;),
			&#34;2&#34; : load_mod(&#34;module/basic/set_security_strategy.py&#34;),
			&#34;999&#34; : load_mod(&#34;module/basic/set_language.py&#34;),
			&#34;1000&#34; : load_mod(&#34;module/basic/get_info.py&#34;),
			&#34;1009&#34; : load_mod(&#34;module/basic/system_status.py&#34;),
			&#34;1014&#34; : load_mod(&#34;module/status/resource.py&#34;),
			&#34;1015&#34; : load_mod(&#34;module/status/fingerprint.py&#34;),
			&#34;1016&#34; : load_mod(&#34;module/hardening/vulscan.py&#34;),
			&#34;1022&#34; : load_mod(&#34;module/hardening/boot_services.py&#34;),
			&#34;1033&#34; : load_mod(&#34;module/terminal/new_pty.py&#34;),
			&#34;1034&#34; : load_mod(&#34;module/terminal/write_pty.py&#34;),
			&#34;1035&#34; : load_mod(&#34;module/terminal/resize_pty.py&#34;),
			&#34;1036&#34; : load_mod(&#34;module/terminal/kill_pty.py&#34;),
			&#34;1037&#34; : load_mod(&#34;module/vnc/init_vnc.py&#34;),
			&#34;1038&#34; : load_mod(&#34;module/hardening/enable_service.py&#34;),
			&#34;1039&#34; : load_mod(&#34;module/status/usage.py&#34;),
			&#34;1040&#34; : load_mod(&#34;module/status/usage_proc.py&#34;),
			&#34;1041&#34; : load_mod(&#34;module/status/user_status.py&#34;),
			&#34;1042&#34; : load_mod(&#34;module/hardening/check_garbage.py&#34;),
			&#34;1043&#34; : load_mod(&#34;module/hardening/clean_garbage.py&#34;),
			#&#34;1044&#34; : load_mod(&#34;module/hardening/remove_garbage.py&#34;),
			&#34;1045&#34; : load_mod(&#34;module/status/network_status.py&#34;),
			&#34;1046&#34; : load_mod(&#34;module/status/cpu_status.py&#34;),
			&#34;1047&#34; : load_mod(&#34;module/status/disk_status.py&#34;),
			#&#34;1048&#34; : load_mod(&#34;module/hardening/cleaner.py&#34;),
			&#34;1049&#34; : load_mod(&#34;module/hardening/security_audit.py&#34;),
			&#34;1050&#34; : load_mod(&#34;module/hardening/check_vuls.py&#34;),
			&#34;1051&#34; : load_mod(&#34;module/hardening/repair_vuls.py&#34;),
			#&#34;1052&#34; : load_mod(&#34;module/hardening/repair_vuls.py&#34;),
			# &#34;1060&#34; : load_mod(&#34;module/filetransfer/sender_init.py&#34;),
			# &#34;1061&#34; : load_mod(&#34;module/filetransfer/udp_setup_server.py&#34;),
			# &#34;1062&#34; : load_mod(&#34;module/filetransfer/udp_setup_client.py&#34;),
			# &#34;1064&#34; : load_mod(&#34;module/filetransfer/udp_punch.py&#34;),
			# &#34;1065&#34; : load_mod(&#34;module/filetransfer/udp_punch_server.py&#34;),
			# &#34;1066&#34; : load_mod(&#34;module/filetransfer/udp_punch_client.py&#34;),
			# &#34;1067&#34; : load_mod(&#34;&#34;
			# &#34;1068&#34; : load_mod(&#34;module/filetransfer/upload.py&#34;),
			# &#34;1069&#34; : load_mod(&#34;module/filetransfer/download.py&#34;),
			&#34;1070&#34; : load_mod(&#34;module/ueba/ueba_overview.py&#34;),
			&#34;1071&#34; : load_mod(&#34;module/ueba/ueba_list.py&#34;),
			&#34;1072&#34; : load_mod(&#34;module/ueba/ueba_detail.py&#34;),
			#&#34;1073&#34; : load_mod(&#34;module/hardening/security_audit_scaner.py&#34;),
			&#34;1074&#34; : load_mod(&#34;module/ueba/ueba_resolve.py&#34;),
			&#34;1075&#34; : load_mod(&#34;module/ueba/ueba_delete_resolved.py&#34;),

			#&#34;1080&#34; : load_mod(&#34;module/filetransfer/list_files.py&#34;),
			#&#34;1081&#34; : load_mod(&#34;sync process&#34;),
			#&#34;1082&#34; : load_mod(&#34;module/filetransfer/downloading.py&#34;),

			&#34;1090&#34; : load_mod(&#34;module/status/get_resource_warnings.py&#34;),
			&#34;1091&#34; : load_mod(&#34;module/status/clear_resource_warnings.py&#34;),
			&#34;1092&#34; : load_mod(&#34;module/status/get_ports.py&#34;),
			&#34;1093&#34; : load_mod(&#34;module/status/get_accounts.py&#34;),
			&#34;1094&#34; : load_mod(&#34;module/status/fresh_ports.py&#34;),
			&#34;1095&#34; : load_mod(&#34;module/status/fresh_accounts.py&#34;),
			&#34;1096&#34; : load_mod(&#34;module/status/remove_port_change.py&#34;),
			&#34;1097&#34; : load_mod(&#34;module/status/remove_account_change.py&#34;),

			&#34;1100&#34; : load_mod(&#34;module/hardening/virusScannerQueryUnhandled.py&#34;),
			&#34;1101&#34; : load_mod(&#34;module/hardening/virusScannerQueryHandled.py&#34;),
			&#34;1102&#34; : load_mod(&#34;module/hardening/virusScannerQueryWhitelist.py&#34;),
			&#34;1103&#34; : load_mod(&#34;module/hardening/virusScannerTrust.py&#34;),
			&#34;1104&#34; : load_mod(&#34;module/hardening/virusScannerDelete.py&#34;),
			&#34;1105&#34; : load_mod(&#34;module/hardening/virusScannerAddWhiteList.py&#34;),
			&#34;1106&#34; : load_mod(&#34;module/hardening/virusScannerDelWhiteList.py&#34;),
			&#34;1107&#34; : load_mod(&#34;module/hardening/virusScannerMoveTo.py&#34;),
			&#34;1108&#34; : load_mod(&#34;module/hardening/virusScannerClearHistory.py&#34;),

			&#34;1119&#34; : load_mod(&#34;module/baseline/get_baseline.py&#34;),
			&#34;1120&#34; : load_mod(&#34;module/baseline/verify.py&#34;),
			&#34;1121&#34; : load_mod(&#34;module/baseline/ignore.py&#34;)
		}

		if common.is_linux():
			self.modules[&#34;1008&#34;] = load_mod(&#34;module/basic/overview.py&#34;)

		if common.is_windows():
			self.modules[&#34;10081&#34;] = load_mod(&#34;module/basic/overview_win.py&#34;)

		if common.is_darwin():
			self.modules[&#34;10082&#34;] = load_mod(&#34;module/basic/overview_mac.py&#34;)

		self.executor = ThreadPoolExecutor(max_workers = 6)
		self.unacked = False

		return True

	def on_unpack(self, *args, **kwargs):
		#data = args[0]
		#import cpacker
		#cpacker.do_unpack(data, self.modules)

		#if self.modules:
		#	Klogger().info(&#34;unpack success {} modules&#34;.format(len(self.modules)))
		#else:
		#	Klogger().error(&#34;unpack failed {} modules&#34;.format(len(self.modules)))

		if not self.unacked:
			self.executor.submit(run_mod, self.modules[&#34;1014&#34;], None, None)
			self.executor.submit(run_mod, self.modules[&#34;1015&#34;], None, None)
			self.executor.submit(run_mod, self.modules[&#34;1016&#34;], None, None)
			#self.executor.submit(run_mod, self.modules[&#34;1048&#34;], None, None)
			#self.executor.submit(run_mod, self.modules[&#34;1073&#34;], None, None)

			self.unacked = True

	def create(self, socket, payload):
		cmd_id = payload[&#34;cmd_id&#34;]

		#You can disable the features you don&#39;t prefer to apply at config/constant.py
		#By default, All features are enabled
		#if cmd_id in constant.ALLOW_MODULE_ID:
		#	if constant.ALLOW_MODULE_ID[cmd_id][&#34;enabled&#34;]:
		if not cmd_id in self.modules:
			Klogger().error(&#34;module {} not found&#34;.format(cmd_id))
			return
		else:
			self.executor.submit(run_mod, self.modules[cmd_id], payload, socket)

	def load_compiled(self, name, filename, code, ispackage = False):
		#if data[:4] != imp.get_magic():
		#	raise ImportError(&#39;Bad magic number in %s&#39; % filename)
		# Ignore timestamp in data[4:8]
		#code = marshal.loads(data[8:])
		imp.acquire_lock() # Required in threaded applications

		try:
			mod = imp.new_module(name)
			sys.modules[name] = mod 	# To handle circular and submodule imports
										# it should come before exec.
			try:
				mod.__file__ = filename # Is not so important.
				# For package you have to set mod.__path__ here.
				# Here I handle simple cases only.
				if ispackage:
					mod.__path__ = [name.replace(&#39;.&#39;, &#39;/&#39;)]
				exec(code in mod.__dict__)
			except:
				del sys.modules[name]
				raise
		finally:
			imp.release_lock()

		return mod
