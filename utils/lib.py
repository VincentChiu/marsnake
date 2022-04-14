# -*- coding: utf-8 -*-
import os
import stat
import time
import re
import socket
import psutil
import struct
from datetime import datetime
from utils import common, file_op

def check_root():
    return os.geteuid() == 0

def get_boot_time():
    if common.check_programs_installed(&#34;systemd-analyze&#34;):
        data, success, retcode = common.exec_command([&#39;systemd-analyze&#39;, &#39;time&#39;])

        if success:
            pattern = re.compile(r&#34;^Startup finished in (.+s) \(kernel\) \+ (.+s) \(initrd\) \+ (.+s) \(userspace\) \= (.+s)&#34;)
            match = pattern.match(data)

            if match:
                groups = list(match.groups())

                if len(groups) == 4:
                    for i in range(len(groups)):
                        index = groups[i].find(&#34;.&#34;)
                        if index &gt;= 0 and len(groups[i][index + 1 : index + 4]) == 3:
                            groups[i] = groups[i][: index + 2] + groups[i][index + 4 :]

                    return tuple(groups)

            pattern = re.compile(r&#34;^Startup finished in (.+s) \(kernel\) \+ (.+s) \(userspace\) \= (.+s)&#34;)
            match = pattern.match(data)

            if match:
                groups = list(match.groups())

                if len(groups) == 3:
                    for i in range(len(groups)):
                        index = groups[i].find(&#34;.&#34;)
                        if index &gt;= 0 and len(groups[i][index + 1 : index + 4]) == 3:
                            groups[i] = groups[i][: index + 2] + groups[i][index + 4 :]
                    return tuple(groups)

    return None

# @kind : 0 for systemd, 1 for upstart, 2 for SysV
def get_description_by_name(service, kind):
    if kind == 0:
        systemd_path = [&#34;/lib/systemd/system/&#34;, &#34;/etc/systemd/system&#34;]
        pattern = re.compile(r&#34;^Description=(.+)&#34;)

        for path in systemd_path:
            unit_path = os.path.join(path, service)

            if os.path.exists(unit_path):
                data = file_op.cat(unit_path, &#34;r&#34;)

                if data:
                    lines = data.split(&#34;\n&#34;)

                    for line in lines:
                        if line:
                            match = pattern.match(line)

                            if match and len(match.groups()):
                                return match.groups()[0]

    if kind == 2:
        des_pattern = re.compile(r&#34;# Description:\s+(.+)&#34;)
        short_pattern = re.compile(r&#34;# Short-Description:\s+(.+)&#34;)
        initscript_path = os.path.join(&#34;/etc/init.d&#34;, service)

        if os.path.exists(initscript_path):
                data = file_op.cat(initscript_path, &#34;r&#34;)

                if data:
                    lines = data.split(&#34;\n&#34;)

                    for line in lines:
                        if line:
                            match = short_pattern.match(line)

                            if match and len(match.groups()):
                                return match.groups()[0]

                            match = des_pattern.match(line)

                            if match and len(match.groups()):
                                return match.groups()[0]

    return &#34;&#34;

def get_ip_gateway():
    route = &#34;/proc/net/route&#34;
    ipv4 = &#34;&#34;
    ipv6 = &#34;&#34;
    gateway = &#34;&#34;
    nic = &#34;&#34;
    RTF_GATEWAY = 0x2

    if os.path.exists(route):
        with open(route, &#34;r&#34;) as f:

            for line in f.readlines():
                route_line = line.split()

                flags = route_line[3]

                if flags.isdigit():
                    flags = int(flags)

                    if flags &amp; RTF_GATEWAY:
                        nic = route_line[0]

                        gateway = route_line[2]
                        gateway = int(gateway, 16)
                        gateway = socket.inet_ntoa(struct.pack(&#34;&lt;I&#34;, gateway))

    if nic != &#34;&#34;:
        interfaces = psutil.net_if_addrs()

        for name, addrs in interfaces.items():
            if name == nic:
                for addr in addrs:
                    if addr[0] == 2:
                        ipv4 = addr[1]

                    if addr[0] == 10:
                        ipv6 = addr[1]

    return nic, ipv4, ipv6, gateway

def find_useradd_users():
    uid_min = 1000
    uid_max = 60000

    data = file_op.cat(&#34;/etc/login.defs&#34;, &#34;r&#34;)

    if data:
        lines = data.split(&#34;\n&#34;)

        for line in lines:
            if line:
                tmp, num = common.grep(line, r&#34;^UID_MIN\s*(\d+)&#34;)
                if num:
                    uid_min = tmp
                    continue

                tmp, num = common.grep(line, r&#34;^UID_MAX\s*(\d+)&#34;)
                if num:
                    uid_max = tmp
                    continue

    data = file_op.cat(&#34;/etc/passwd&#34;, &#34;r&#34;)
    usernames = []

    if data:
        lines = data.split(&#34;\n&#34;)

        for line in lines:
            if line:
                username, password, uid, gid, comment, home, shell = line.split(&#34;:&#34;)

                if uid_min != None and uid_max != None:
                    if int(uid) &gt;= int(uid_min) and int(uid) &lt;= int(uid_max):
                        usernames.append(username)

    return usernames

def timestamp2count(tickcount):
    s = time.strftime(&#39;%Y-%m-%d %H:%M:%S&#39;, time.localtime(tickcount))
    new_s = &#34;%04d-%02d-%02d %02d:%02d:%02d&#34; % (int(s[:4]) - 1970,
                                            int(s[5:7]) - 1, int(s[8:10]) - 1,
                                            int(s[11:13]) - 8, int(s[14:16]), int(s[17:]))
    return new_s

def time_duration(start_timestamp, end_timestamp):
    start = datetime.fromtimestamp(start_timestamp)
    end = datetime.fromtimestamp(end_timestamp)

    return end - start

def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
                (&#39;year&#39;,    60 * 60 * 24 * 365),
                (&#39;month&#39;,   60 * 60 * 24 * 30),
                (&#39;day&#39;,     60 * 60 * 24),
                (&#39;hour&#39;,    60 * 60),
                (&#39;minute&#39;,  60),
                (&#39;second&#39;,  1)
            ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds &gt; period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)

            if period_value == 1:
                strings.append(&#34;%s %s&#34; % (period_value, period_name))
            else:
                strings.append(&#34;%s %ss&#34; % (period_value, period_name))

    return &#34;, &#34;.join(strings)

def special_to_letter(mode):
    l = &#39;&#39;

    ALL_R = (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    ALL_W = (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

    if mode &amp; stat.S_ISGID:
        l += &#39;G&#39;
    if mode &amp; stat.S_ISUID:
        l += &#39;U&#39;
    if mode &amp; stat.S_ISVTX:
        l += &#39;T&#39;
    if mode &amp; (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        l += &#39;E&#39;
    if ( mode &amp; ALL_R ) == ALL_R:
        l += &#39;R&#39;
    if ( mode &amp; ALL_W ) == ALL_W:
        l += &#39;W&#39;

    return l

def permissions_to_unix_name(mode):
    is_dir = &#39;d&#39; if stat.S_ISDIR(mode) else &#39;-&#39;
    dic = {&#39;7&#39;:&#39;rwx&#39;, &#39;6&#39; :&#39;rw-&#39;, &#39;5&#39; : &#39;r-x&#39;, &#39;4&#39;:&#39;r--&#39;, &#39;3&#39;:&#39;-wx&#39;, &#39;2&#39;:&#39;-w-&#39;, &#39;1&#39;:&#39;--x&#39;, &#39;0&#39;: &#39;---&#39;}
    perm = str(oct(mode)[-3 : ])

    return is_dir + &#39;&#39;.join(dic.get(x, x) for x in perm)

#/etc/os-release -&gt; ../usr/lib/os-release
#/usr/lib/os-release -&gt; ./os.release.d/os-release-workstation
def readlink(path, depth):
    result = &#34;&#34;

    while True:
        if not os.path.exists(path):
            path = &#34;&#34;
            break

        _stat = os.lstat(path)

        if stat.S_ISLNK(_stat.st_mode):
            result = os.readlink(path)
        else:
            break

        if not os.path.isabs(result):
            path = os.path.join(os.path.dirname(path), result)  #/etc/../usr/lib/os-release
        else:
            path = result

        depth -= 1

        if depth == 0:
            break

    return path

def check_world_writable(path):
    try:
        _stat = os.stat(path)

        if _stat.st_mode &amp; stat.S_IWOTH:
            return True

    except Exception as e:
        pass

    return False

def check_access_writable(path):
    return os.access(path, os.W_OK)

#https://unix.stackexchange.com/questions/139764/what-are-the-world-writable-directories-by-default
def find_writable_dir():
    writable_path = [&#34;/tmp&#34;, &#34;/var/tmp&#34;, &#34;/dev/shm&#34;]
    path = &#34;&#34;

    for tmp in writable_path:
        if check_access_writable(tmp):
            path = tmp
            break

    return path

def detect_debian_like_os():
     #debian
    data, success, retcode = common.exec_command([&#39;ls&#39;, &#39;/etc/debian_version&#39;])
    if success:
        return True

    return False

def detect_distribution():

    distro = &#34;&#34;
    distro_release = &#34;&#34;

    #os-release
    #https://www.freedesktop.org/software/systemd/man/os-release.html
    #NAME=&#34;Ubuntu&#34;
    #VERSION=&#34;16.04.2 LTS (Xenial Xerus)&#34;
    items = {&#34;NAME&#34; : None, &#34;VERSION&#34; : None}
    data = file_op.cat(&#39;/etc/os-release&#39;, &#39;r&#39;)

    if data:
        lines = data.split(&#34;\n&#34;)

        for line in lines:
            if line:
                k, v = line.split(&#34;=&#34;)

                if k in items:
                    items[k] = v.lstrip(&#39;&#34;&#39;).rstrip(&#39;&#34;&#39;)

        distro = items[&#34;NAME&#34;]
        distro_release = items[&#34;VERSION&#34;]

        if distro and distro_release:
            return distro, distro_release

    #fedora, oracle, centos, amazon
    #https://www.rackaid.com/blog/how-to-determine-centos-or-red-hat-version/
    #Fedora release 26 (Twenty Six)
    #CentOS Linux release 7.3.1611 (Core)
    #Amazon Linux AMI release 2017.03
    identification = [&#34;/etc/fedora-release&#34;, &#34;/etc/oracle-release&#34;, &#34;/etc/redhat-release&#34;, &#34;/etc/system-release&#34;]

    for i in identification:
        if os.path.exists(i):
            data = file_op.cat(i, &#39;r&#39;)

            if data:
                pattern = re.compile(r&#39;(.*) release (\d[\d.]*)&#39;)
                match = pattern.match(data)

                if len(match.groups()) == 2:
                    distro = match.groups()[0]
                    distro_release = match.groups()[1]

                    if distro and distro_release:
                        return distro, distro_release

    data = file_op.cat(&#39;/etc/issue&#39;, &#39;r&#39;)

    #raspbian
    if success:
        result = data.split()

        if len(result) &gt; 2 and result[0] == &#34;Raspbian&#34;:
            distro = &#34;raspbian&#34;
            return True

    data, success, retcode = common.exec_command([&#39;lsb_release&#39;, &#39;-ir&#39;])

    #Distributor ID: Ubuntu
    #Release:        16.04
    if success:
        pattern = re.compile(r&#39;(?s)^Distributor ID:\s*(.+?)\n*Release:\s*(.+?)$&#39;)
        match = pattern.match(data)

        if len(match.groups()) == 2:
            distro = match.groups()[0]
            distro_release = match.groups()[1]

            if distro and distro_release:
                return distro, distro_release

    data = file_op.cat(&#39;/etc/lsb-release&#39;, &#39;r&#39;)

    #DISTRIB_ID=Ubuntu
    #DISTRIB_RELEASE=16.04
    #DISTRIB_CODENAME=xenial
    #DISTRIB_DESCRIPTION=&#34;Ubuntu 16.04.2 LTS&#34;
    if success:
        pattern = re.compile(r&#39;(?s)^DISTRIB_ID=(.+?)\n*DISTRIB_RELEASE=(.+?)\n.*$&#39;)
        match = pattern.match(data)

        if len(match.groups()) == 2:
            distro = match.groups()[0]
            distro_release = match.groups()[1]

            if distro and distro_release:
                return distro, distro_release

    distro = platform.linux_distribution()[0]
    distro_release = platform.linux_distribution()[1]

    return distro, distro_release
