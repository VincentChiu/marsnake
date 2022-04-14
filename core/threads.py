from utils.singleton import singleton

import threading
import inspect
import ctypes

def _async_raise(tid, exctype):
	&#34;&#34;&#34;raises the exception, performs cleanup if needed&#34;&#34;&#34;
	if not inspect.isclass(exctype):
		raise TypeError(&#34;Only types can be raised (not instances)&#34;)

	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

	if res == 0:
		raise ValueError(&#34;invalid thread id&#34;)
	elif res != 1:
		# &#34;&#34;&#34;if it returns a number greater than one, you&#39;re in trouble,
		# and you should call it again with exc=NULL to revert the effect&#34;&#34;&#34;
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
		raise SystemError(&#34;PyThreadState_SetAsyncExc failed&#34;)

class Thread(threading.Thread):
	def _get_my_tid(self):
		&#34;&#34;&#34;determines this (self&#39;s) thread id&#34;&#34;&#34;
		if not self.isAlive():
			raise threading.ThreadError(&#34;the thread is not active&#34;)

		# do we have it cached?
		if hasattr(self, &#34;_thread_id&#34;):
			return self._thread_id

		# no, look for it in the _active dict
		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = tid
				return tid

		raise AssertionError(&#34;could not determine the thread&#39;s id&#34;)

	def raise_exc(self, exctype):
		&#34;&#34;&#34;raises the given exception type in the context of this thread&#34;&#34;&#34;
		_async_raise(self._get_my_tid(), exctype)

	def terminate(self):
		&#34;&#34;&#34;raises SystemExit in the context of the given thread, which should
		cause the thread to exit silently (unless caught)&#34;&#34;&#34;
		self.raise_exc(SystemExit)

@singleton
class Kthreads(object):
	def __init__(self):
		self.thread_pool = []

	def apply_async(self, func, args):
		t = Thread(target = func, args = args)

		t.daemon = True
		t.start()

		self.thread_pool.append(t)

	def interrupt_all(self):
		for t in self.thread_pool:
			if t.isAlive():
				t.terminate()

	def join(self):
		while True:
			try:
				allok = True

				for t in self.thread_pool:
					if t.isAlive():
						t.join(0.5)
						allok = False

				if allok:
					break
			except KeyboardInterrupt:
				print(&#34;Press [ENTER] to interrupt the job&#34;)
				#self.interrupt_all()
				break

	def all_finished(self):
		for t in self.thread_pool:
			if t.isAlive():
				return False

		return True

	def get_name(self):
		return threading.currentThread().name

	def set_name(self, name):
		threading.currentThread().setName(name)

	def set_daemon(self):
		threading.currentThread().setDaemon(True)

	def is_daemon(self):
		return threading.currentThread().isDaemon()
