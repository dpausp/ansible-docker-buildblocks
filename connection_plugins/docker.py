# Connection plugin for configuring docker containers
# Author: Lorin Hochstein
#
# Based on the chroot connection plugin by Maykel Moya
from __future__ import print_function
import os
import sys
import subprocess
import time

from ansible import errors
from ansible.callbacks import vvv, vvvv


class Connection(object):
    def __init__(self, runner, host, port, *args, **kwargs):
        self.host = host
        self.runner = runner
        self.has_pipelining = False
        self.docker_cmd = "docker"

    def connect(self, port=None):
        """ Connect to the container. Nothing to do """
        return self

    def exec_command(self, cmd, tmp_path, sudo_user=None, sudoable=False, become_user=None,
                     executable='/bin/sh', in_data=None, su=None,
                     su_user=None):


#        print(cmd, tmp_path, sudo_user, sudoable, executable, in_data, su)

        """ Run a command on the local host """

        # Don't currently support su
        if su or su_user:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support running commands via su")

        if in_data:
            raise errors.AnsibleError("Internal Error: this module does not "
                                      "support optimized module pipelining")

        if sudoable and sudo_user and self.runner.sudo:
            cmd = "sudo -H -i -u %s %s" % (sudo_user, cmd)

        if executable:
            local_cmd = [self.docker_cmd, "exec", self.host, executable,
                         '-c', cmd]
        else:
            local_cmd = '%s exec "%s" env %s' % (self.docker_cmd, self.host, cmd)
        
        vvv("EXEC %s" % (local_cmd), host=self.host)
        p = subprocess.Popen(local_cmd,
                             shell=isinstance(local_cmd, basestring),
                             cwd=self.runner.basedir,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        return (p.returncode, '', stdout, stderr)

    # Docker doesn't have native support for copying files into running
    # containers, so we use docker exec to implement this
    def put_file(self, in_path, out_path):
        """ Transfer a file from local to container """
        args = [self.docker_cmd, "exec", "-i", self.host, "sh", "-c",
                "cat > {0}".format(out_path)]

        vvv("PUT %s TO %s" % (in_path, out_path), host=self.host)

        if not os.path.exists(in_path):
            raise errors.AnsibleFileNotFound(
                "file or module does not exist: %s" % in_path)

        with open(in_path) as f:
            p = subprocess.Popen(args, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # XXX: testing
        args = [self.docker_cmd, "exec", self.host, "stat", "-c %s", out_path]
        orig_size = os.stat(in_path).st_size
        cc = 0
        while 1:
            cc += 1
            if cc > 1:
                print("retry: " + str(cc))
            p_stat = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p_stat.communicate()
            try:
                dest_size = int(stdout.strip())
            except:
                print("no target size, wait a bit...", file=sys.stderr)
                time.sleep(0.05)
            else:
                if dest_size != orig_size:
                    print("src and dest size do not match: {} {}, wait a bit...".format(dest_size, orig_size), file=sys.stderr)
                    time.sleep(0.05)
                else:
                    break
        
        # XXX: don't know why, but cat seems to hang in some cases (?)
        subprocess.Popen([self.docker_cmd, "exec", self.host, "killall", "cat"], stderr=subprocess.PIPE).communicate()


    def fetch_file(self, in_path, out_path):
        """ Fetch a file from container to local. """
        # out_path is the final file path, but docker takes a directory, not a
        # file path
        out_dir = os.path.dirname(out_path)
        args = [self.docker_cmd, "cp", "%s:%s" % (self.host, in_path), out_dir]

        vvv("FETCH %s TO %s" % (in_path, out_path), host=self.host)
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # Rename if needed
        actual_out_path = os.path.join(out_dir, os.path.basename(in_path))
        if actual_out_path != out_path:
            os.rename(actual_out_path, out_path)

    def close(self):
        """ Terminate the connection. Nothing to do for Docker"""
        pass
