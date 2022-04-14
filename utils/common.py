import sys, socket, os, platform, locale, re, psutil, glob, subprocess, multiprocessing, uuid, hashlib, hmac
from config import constant

system = sys.platform
os_encoding = locale.getpreferredencoding() or &#34;utf8&#34;
work_dir = &#34;&#34;

def fork_process(target, args):
	return multiprocessing.Process(target = target, args = args)

def exec_command(cmd):
	cmdstr = &#39; &#39;.join(cmd)
	process = subprocess.Popen(cmdstr, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
	stdout, stderr = process.communicate()

	if process.returncode == 0:
		return str(stdout).strip() if is_python2x() else stdout.decode(os_encoding).strip(), True, process.returncode
	else:
		return str(stderr).strip() if is_python2x() else stderr.decode(os_encoding).strip(), False, process.returncode
		#raise Exception(&#34;stderr: %s&#34; % str(stderr))

def create_uuid():
	return str(uuid.uuid1())

def check_obj_is_string(s):
	if is_python2x():
		return isinstance(s, basestring)
	else:
		return isinstance(s, str)

def decode2utf8(data):
	if is_python2x():
		if isinstance(data, str):
			return data.decode(os_encoding)
		else:
			return data
	else:
		if isinstance(data, bytes):
			return data.decode(os_encoding)
		else:
			return data

def print_obj(obj):
	print(&#39;\n&#39;.join([&#39;%s:%s&#39; % item for item in obj.__dict__.items()]))

def add_module_path(path):
	sys.path.append(os.path.join(get_work_dir(), path))

def print2hex(s):
	print(&#34;:&#34;.join(&#34;{:02x}&#34;.format(ord(c)) for c in s))

def is_python2x():
	return sys.version_info  &lt; (3, 0)

def setdefaultencoding(coding):
	if sys.version_info  &lt; (3, 0):
		reload(sys)
		sys.setdefaultencoding(coding)

def python_version(version):
	return sys.version_info.major == version

def set_work_dir():
	global work_dir
	
	if hasattr(sys, &#34;frozen&#34;):# synchronize with pyloader&#39;s initialization.py
		#work_dir = os.path.abspath(os.path.join(os.path.dirname(os.__file__),&#39;..&#39;))
		work_dir = os.path.abspath(os.path.join(os.path.dirname(os.__file__)))
	else:
		work_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), &#34;..&#34;))

def get_work_dir():
	global work_dir
	return work_dir

def get_data_location():
	data_dir = None

	if is_windows():
		data_location = os.getenv(&#39;APPDATA&#39;)

		if not os.path.exists(data_location):
			try:
				from win32com.shell import shellcon, shell
				data_location = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)

			except ImportError: # quick semi-nasty fallback for non-windows/win32com case
				data_location = os.path.expanduser(&#34;~&#34;)

		data_dir = os.path.join(data_location, constant.APP_NAME)

		if not os.path.exists(data_dir):
			os.mkdir(data_dir)

	if is_linux() or is_darwin():
		home = path_translate(&#34;~&#34;)
		data_dir = os.path.join(home, &#34;.{}&#34;.format(constant.APP_NAME))

		if not os.path.exists(data_dir):
			os.mkdir(data_dir)

	return data_dir

def is_linux():
	global system
	return system == &#34;linux2&#34; or system == &#34;linux&#34;

def is_windows():
	global system
	return system == &#34;win32&#34;

def is_darwin():
	global system
	return system == &#34;darwin&#34;

def is_x86_64():
	return platform.machine() == &#39;x86_64&#39;

def extend_at_front(array_src, maxi, cons):
	array_dst = array_src[-maxi : len(array_src)]
	diff = maxi - len(array_dst)

	if diff:
		tmp = [ cons for x in range(diff) ]
		tmp.extend(array_dst)
		array_dst = tmp

	return array_dst

def boolstr_to_bool(value):
	&#34;&#34;&#34;Convert a string boolean to a Python boolean&#34;&#34;&#34;
	if &#39;true&#39; == value.lower():
		return True

	if &#39;false&#39; == value.lower():
		return False

	raise RuntimeError(&#34;Invalid boolean: &#39;%s&#39;&#34; % value)

def do_get_ip_gateway():
	ip = &#39;127.0.0.1&#39;
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setblocking(0)

	try:
		# doesn&#39;t even have to be reachable
		s.connect((&#39;10.255.255.255&#39;, 1))
		ip = s.getsockname()[0]
	except:
		pass
	finally:
		s.close()

	return ip

def get_ip_gateway():

	if is_windows():
		return do_get_ip_gateway()
	elif is_linux():
		from utils import lib
		return lib.get_ip_gateway()[1] or do_get_ip_gateway()
	elif is_darwin():
		return do_get_ip_gateway()

	return &#34;&#34;

def get_distribution():

	if is_windows():
		if sys.version_info[0] == 2:
			import _winreg
		else:
			import winreg as _winreg

		reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, &#34;SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion&#34;)
		info = _winreg.QueryValueEx(reg_key, &#34;ProductName&#34;)[0]

		if info:
			return info
		else:
			return &#34;Windows {}&#34;.format(platform.win32_ver()[0])

	elif is_linux():
		from utils import lib
		return &#34;{} {}&#34;.format(*(lib.detect_distribution()))

	elif is_darwin():
		return &#34;MacOS X {}&#34;.format(platform.mac_ver()[0])

	return &#34;&#34;

def grep(line, pattern):
	sub = re.findall(pattern, line)

	if len(sub) != 0:
		return sub[0], len(sub)
	else:
		return &#34;&#34;, 0

def size_human_readable(num, suffix = &#39;B&#39;):
	try:
		num = int(num)
		for unit in [&#39;&#39;,&#39;Ki&#39;,&#39;Mi&#39;,&#39;Gi&#39;,&#39;Ti&#39;,&#39;Pi&#39;,&#39;Ei&#39;,&#39;Zi&#39;]:
			if abs(num) &lt; 1024.0:
				return &#34;%3.1f %s%s&#34; % (num, unit, suffix)
			num /= 1024.0
		return &#34;%.1f %s%s&#34; % (num, &#39;Yi&#39;, suffix)
	except:
		return &#39;0.00 B&#39;

def try_unicode(path):
	if not isinstance(path, unicode if is_python2x() else str):
		try:
			return path.decode(os_encoding)
		except UnicodeDecodeError:
			pass

	return path

def is_program_running(program):
	program = program.lower()

	if is_linux():
		&#34;&#34;&#34;Check whether program is running&#34;&#34;&#34;
		for filename in glob.iglob(&#34;/proc/*/exe&#34;):
			try:
				target = os.path.realpath(filename)
			except TypeError:
				# happens, for example, when link points to
				# &#39;/etc/password\x00 (deleted)&#39;
				continue
			except OSError:
				# 13 = permission denied
				continue

			if program == os.path.basename(target):
				return True

		return False

	elif is_darwin():
		def run_ps():
			subprocess.check_output([&#34;ps&#34;, &#34;aux&#34;, &#34;-c&#34;])

		try:
			processess = (re.split(r&#34;\s+&#34;, p, 10)[10] for p in run_ps().split(&#34;\n&#34;) if p != &#34;&#34;)
			next(processess)  # drop the header
			return program in processess
		except IndexError:
			pass

		return False

	else:
		for proc in psutil.process_iter():
			try:
				if proc.name().lower() == program:
					return True
			except psutil.NoSuchProcess:
				pass

		return False

def get_listen_port(ports):
	conns = psutil.net_connections(kind = &#34;inet&#34;)
	ret = []

	for conn in conns:
		fd, family, _type, laddr, raddr, status, pid = conn

		if status == &#34;LISTEN&#34;:
			port = laddr[1]

			if port in ports:
				ret.append(port)

	return list(set(ret))

def is_kernel_thread(proc):
	if is_linux():
		&#34;&#34;&#34;Return True if proc is a kernel thread, False instead.&#34;&#34;&#34;
		try:
			return os.getpgid(proc.pid) == 0
		# Python &gt;= 3.3 raises ProcessLookupError, which inherits OSError
		except OSError:
			# return False is process is dead
			return False

	elif is_windows():
		return proc.pid == 0 or proc.pid == 4

	return False

#5.2 M
def sizestring2int(sstr):
	pattern = re.compile(r&#34;(\S+)\s(\w)&#34;)
	match = pattern.match(sstr.strip())
	size = 0

	if match and len(match.groups()) == 2:
		size = float(match.groups()[0])
		unit = match.groups()[1].lower()

		if unit == &#39;m&#39;:
			size *= 1024 * 1024
		elif unit == &#39;k&#39;:
			size *= 1024

	return int(size)

# os.path.expandvars does not work well with non-ascii Windows paths.
# This is a unicode-compatible reimplementation of that function.
def expandvars(var):
	&#34;&#34;&#34;Expand environment variables.

	Return the argument with environment variables expanded. Substrings of the
	form $name or ${name} or %name% are replaced by the value of environment
	variable name.&#34;&#34;&#34;
	if is_python2x() and isinstance(var, str):
		final = var.decode(&#39;utf-8&#39;)
	else:
		final = var

	if &#39;posix&#39; == os.name:
		final = os.path.expandvars(final)
	elif &#39;nt&#39; == os.name:
		if sys.version_info[0] == 2:
			import _winreg
		else:
			import winreg as _winreg
		if final.startswith(&#39;${&#39;):
			final = re.sub(r&#39;\$\{(.*?)\}(?=$|\\)&#39;,
						   lambda x: &#39;%%%s%%&#39; % x.group(1),
						   final)
		elif final.startswith(&#39;$&#39;):
			final = re.sub(r&#39;\$(.*?)(?=$|\\)&#39;,
						   lambda x: &#39;%%%s%%&#39; % x.group(1),
						   final)
		final = _winreg.ExpandEnvironmentStrings(final)
	return final

def path_translate(path):
	path = try_unicode(path)
	path = os.path.expanduser(path)
	path = os.path.expandvars(path)

	return path

# Windows paths have to be unicode, but os.path.expanduser does not support it.
# This is a unicode-compatible reimplementation of that function.
def expanduser(path):
	&#34;&#34;&#34;Expand the path with the home directory.

	Return the argument with an initial component of &#34;~&#34; replaced by
	that user&#39;s home directory.
	&#34;&#34;&#34;
	if is_python2x() and isinstance(path, str):
		final = path.decode(&#39;utf-8&#39;)
	else:
		final = path

	# If does not begin with tilde, do not alter.
	if len(path) == 0 or not &#39;~&#39; == path[0]:
		return final

	if &#39;posix&#39; == os.name:
		final = os.path.expanduser(final)
	elif &#39;nt&#39; == os.name:
		found = False
		for env in [u&#39;%USERPROFILE%&#39;, u&#39;%HOME%&#39;]:
			if env in os.environ:
				home = expandvars(env)
				found = True
				break
		if not found:
			h_drive = expandvars(u&#39;%HOMEDRIVE%&#39;)
			h_path = expandvars(u&#39;%HOMEPATH%&#39;)
			home = os.path.join(h_drive, h_path)
		final = final.replace(&#39;~user/&#39;, &#39;&#39;)
		final = final.replace(&#39;~/&#39;, &#39;&#39;)
		final = final.replace(&#39;~&#39;, &#39;&#39;)
		final = os.path.join(home, final)
	return final

def check_programs_installed(program):
	delimiter = &#39;:&#39;

	if &#39;nt&#39; == os.name:
		delimiter = &#39;;&#39;

	for path in os.environ[&#34;PATH&#34;].split(delimiter):
		if os.path.exists(path):
			try:
				for x in os.listdir(path):
					item = os.path.join(path, x)

					if os.path.isfile(item):
						if x == program:
							return True
			except Exception as e:
				pass

	return False

def contain_in_string(containVar, stringVar):
	try:
		if isinstance(stringVar, str):
			if stringVar.find(containVar) &gt; -1:
				return True
			else:
				return False
		else:
			return False
	except Exception as e:
		print(e)

def md5(content):
	m = hashlib.md5()
	m.update(content.encode())

	return m.hexdigest()

def sha256(content):
	sha = hashlib.sha256()
	sha.update(content.encode())

	return sha.hexdigest()

def sha256_hmac(content):
	h = hmac.new(content.encode(), digestmod = hashlib.sha256)

	return h.hexdigest()
