# -*- coding: utf-8 -*-
from Arya.backends.base_module import BaseSaltMoude


class Group(BaseSaltMoude):
    def gid(self, *args, **kwargs):
        self.argv_validation('gid', args[0], int)
        cmd = '-g %s' % args[0]

        self.raw_cmds.append(cmd)
        return cmd

    def present(self, *args, **kwargs):
        """
        拼接命令
        :param args:
        :param kwargs:
        :return:
        """
        cmd_list = []
        username = kwargs.get('section')
        self.raw_cmds.insert(0, 'useradd %s' % username)

        cmd_list.append(' '.join(self.raw_cmds))
        cmd_list.extend(self.single_line_cmds)
        print('\033[0;41mcmd_list: \033[0m', cmd_list)
        return cmd_list

    def is_reuqired(self, *args, **kwargs):
        name = args[1]
        cmd = """more /etc/group | awk -F ":" '{print $1}' | grep -w %s -q;echo $?""" % name
        return cmd
