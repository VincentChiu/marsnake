from utils.singleton import singleton
from utils import common, net_op
from core.security import Ksecurity
from core.logger import Klogger
import re, json, base64

@singleton
class Khttp():
	def __init__(self):
		pass

	def get_connection(self, addr, userID):
		host = None
		port = None

		data = &#34;{};{}&#34;.format(userID, Ksecurity().get_pubkey())
		encrypt = Ksecurity().rsa_long_encrypt(data)

		Klogger().info(&#34;Request to Web server {} userid:{}&#34;.format(addr, userID))
		status, data = net_op.create_http_request(addr, &#34;POST&#34;, &#34;/get_logic_conn&#34;, encrypt)
		Klogger().info(&#34;Get Response From Gateway server status({})&#34;.format(status))

		if status == 200:
			data = json.loads(data)
			
			if data[&#34;code&#34;] == 0:
				destination = Ksecurity().rsa_long_decrypt(base64.b64decode(data[&#34;data&#34;]))

				if b&#34;:&#34; in destination:
					host, port = destination.split(b&#34;:&#34;, 1)
					host = host.decode(&#34;ascii&#34;)
					port = port.decode(&#34;ascii&#34;)

				Klogger().info(&#34;Logic Server Host:{} Port:{}&#34;.format(host, port))
			else:
				Klogger().info(&#34;Connect to Web server failed:{}&#34;.format(data[&#34;msg&#34;]))

		return host, port