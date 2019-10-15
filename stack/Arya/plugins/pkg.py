# -*- coding: utf-8 -*-
from Arya.backends.base_module import BaseSaltMoude


class Pkg(BaseSaltMoude):
    def is_reuqired(self, *args, **kwargs):
        name = args[1]
        cmd = """more /etc/group | awk -F ":" '{print $1}' | grep -w %s -q;echo $?""" % name
        return cmd