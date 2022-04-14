from utils.singleton import singleton

import random, string

@singleton
class Krandom(object):
	def __init__(self):
		pass

	def uppercase(self, length):
		seq = string.ascii_uppercase
		return &#39;&#39;.join(random.choice(seq) for _ in range(length))

	def lowercase(self, length):
		seq = string.ascii_lowercase
		return &#39;&#39;.join(random.choice(seq) for _ in range(length))
		
	def purely(self, length):
		seq = string.ascii_uppercase + string.digits + string.ascii_lowercase
		return &#39;&#39;.join(random.choice(seq) for _ in range(length))

	def digits(self, length):
		seq = string.digits
		return &#39;&#39;.join(random.choice(seq) for _ in range(length))

	def randint(self, min, max):
		return random.randint(min, max)
