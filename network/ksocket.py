from module.factory_module import Kmodules
from utils.randomize import Krandom
from utils import common
from config import constant
from ctypes import create_string_buffer
from core.security import Ksecurity
from core.logger import Klogger
from core.event import Kevent
import socket, json, struct, threading

class stream():
	def __init__(self, size):
		self.buffer = create_string_buffer(size)
		self.size = size
		self.index = 0

	def write(self, data):
		if self.index + len(data) &gt; self.size:
			Klogger().error(&#34;index:{} len(data):{} size:{}&#34;.format(self.index, len(data), self.size))
			raise

		for i in range(len(data)):
			self.buffer[self.index] = data[i]
			self.index += 1

	def get_len(self):
		return self.index

	def get_data(self, start, wanted):
		if self.index &lt; start + wanted:
			return None

		return self.buffer[start:start + wanted]

	def clear(self, total):
		diff = self.index - total

		if diff == 0:
			self.index = 0
			return
		elif diff &gt; 0:
			for i in range(diff):
				self.buffer[i] = self.buffer[total + i]

			self.index = diff
		else:
			raise &#34;diff({}) &lt; 0&#34;.format(diff)

class Ksocket():
	def __init__(self, host, port, userid, nodelay = False, keepalive = True):
		self.host = host
		self.port = port
		self.userid = userid

		self.family = socket.AF_INET
		self.type = socket.SOCK_STREAM

		self.nodelay = nodelay
		self.keepalive = keepalive

		self.input = stream(constant.SOCKET_BUFFER_SIZE)
		#self.output = stream(constant.SOCKET_BUFFER_SIZE)

		self.lock = threading.Lock()

	def start(self):
		family, socktype, proto, _, sockaddr = socket.getaddrinfo(self.host, self.port, self.family, self.type)[0]

		sock = socket.socket(family, socktype)
		sock.connect(sockaddr)

		if self.nodelay:
			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		if self.keepalive:
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

		if hasattr(socket, &#34;TCP_KEEPIDLE&#34;) and hasattr(socket, &#34;TCP_KEEPINTVL&#34;) and hasattr(socket, &#34;TCP_KEEPCNT&#34;):
			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1 * 60)
			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
		elif hasattr(socket, &#34;SIO_KEEPALIVE_VALS&#34;):
			sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 1 * 60 * 1000, 5 * 60 * 1000))

		self.sock = sock
		self.recv_count = 0

		Ksecurity().reset_aes()

	def loop(self):
		while True:
			request = self.sock.recv(constant.SOCKET_RECV_SIZE)

			if not len(request):
				Kevent().do_disconnected()
				break;

			self.input.write(request)
			#self.print2hex(self.input.get_data(0, self.input.get_len()))

			while self.handle_package():
				pass

	def handle_package(self):
		recv_len = self.input.get_len()

		if recv_len &lt; 36:
			return False

		plen = self.input.get_data(32, 4)
		plen = struct.unpack(&#39;&gt;I&#39;, plen)[0]

		total = 32 + 4 + plen + 16

		if recv_len &lt; total:
			return False

		payload = self.input.get_data(36, plen)
		self.input.clear(total)

		self.handle_package_2(payload)

		return True

	def handle_package_2(self, payload):
		if self.recv_count == 0:
			payload = json.loads(payload)
			Klogger().info(&#34;recv:{}&#34;.format(payload))

			if payload[&#34;cmd_id&#34;] == &#34;10000&#34;:
				Ksecurity().swap_publickey_with_server(self)

		elif self.recv_count == 1:
			payload = json.loads(payload)
			Klogger().info(&#34;recv:{}&#34;.format(payload))

			if payload[&#34;cmd_id&#34;] == &#34;1000&#34;:
				payload[&#34;user_id&#34;] = self.userid
				Kmodules().create(self, payload)
		else:
			payload = Ksecurity().aes_decrypt(payload)
			payload = json.loads(payload)

			if payload[&#34;cmd_id&#34;] in [&#34;1000&#34;]:
				Klogger().info(&#34;recv:{}&#34;.format(payload))

			#if payload[&#34;args&#34;][&#34;user_id&#34;] == self.userid:
			Kmodules().create(self, payload)

		self.recv_count += 1

	def response(self, payload):
		try:
			with self.lock:
				if payload[&#34;cmd_id&#34;] in [&#34;1000&#34;]:
					Klogger().info(payload)

				prefix = struct.pack(&#34;32s&#34;, Krandom().purely(32).encode(&#34;ascii&#34;))
				suffix = struct.pack(&#34;16s&#34;, Krandom().purely(16).encode(&#34;ascii&#34;))
				payload = json.dumps(payload).encode(&#34;ascii&#34;)

				if Ksecurity().can_aes_encrypt():
					payload = Ksecurity().aes_encrypt(payload)

				payload_len = struct.pack(&#34;&lt;I&#34;, len(payload))

				data = prefix + payload_len + payload + suffix
				datalen = len(data)
				send_bytes = 0

				while send_bytes &lt; datalen:
					send_bytes += self.sock.send(data[send_bytes:])

		except Exception as e:
			Klogger().exception()

	def close(self):
		if hasattr(self, &#34;sock&#34;):
			self.sock.close()
