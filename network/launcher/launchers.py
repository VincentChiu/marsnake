import sys
from utils.singleton import singleton

@singleton
class Klauncher():
	&#34;class launcher&#34;
	def __init__(self):
		from network.launcher.connect_launcher import connect_launcher
		
		self.launcher = None
		self.map = {
			&#34;connect&#34; : connect_launcher
		}
	
	def on_initializing(self, *args, **kwargs):
		name = &#34;connect&#34;

		if not name in self.map.keys():
			return False				#assert 0, &#34;bad launcher name&#34;
			
		self.launcher = self.map[name]()
		
		return True
		
	def on_start(self, *args, **kwargs):
		if self.launcher:
			self.launcher.start()

	def get_names(self):
		return self.map.keys()