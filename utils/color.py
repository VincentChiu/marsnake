from . import common
import random

def colorize(s, color):
    if s is None:
        return &#34;&#34;

    if not isinstance(s, (str, unicode) if common.is_python2x() else (str, bytes)):
        s = str(s)

    res = s
    COLOR_STOP = &#34;\033[0m&#34;

    if color.lower() == &#34;random&#34;:
        color = random.choice([&#34;blue&#34;,&#34;red&#34;,&#34;green&#34;,&#34;yellow&#34;])

    if color.lower() == &#34;blue&#34;:
        res = &#34;\033[34m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;red&#34;:
        res = &#34;\033[31m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;lightred&#34;:
        res = &#34;\033[31;1m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;green&#34;:
        res = &#34;\033[32m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;lightgreen&#34;:
        res = &#34;\033[32;1m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;yellow&#34;:
        res = &#34;\033[33m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;lightyellow&#34;:
        res = &#34;\033[1;33m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;magenta&#34;:
        res = &#34;\033[35m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;cyan&#34;:
        res = &#34;\033[36m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;grey&#34;:
        res = &#34;\033[37m&#34; + s + COLOR_STOP
    elif color.lower() == &#34;darkgrey&#34;:
        res = &#34;\033[1;30m&#34; + s + COLOR_STOP

    return res
