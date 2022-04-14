class base_launcher(object):
	def __init__(self):
		pass
		
	def init_argparse(self, args):
		raise NotImplementedError(&#34;init_argparse launcher&#39;s method needs to be implemented&#34;)
		
	def print_argparser(self):
		self.parser.print_help()
		
	def start(self):
		raise NotImplementedError(&#34;start launcher&#39;s method needs to be implemented&#34;)