# -*- coding: utf-8 -*-
from Arya.backends.base_module import BaseSaltMoude


class User(BaseSaltMoude):
    def uid(self, *args, **kwargs):
        self.argv_validation('uid', args[0], int)
        cmd = '-u %s' % args[0]
        self.raw_cmds.append(cmd)

        return cmd

    def gid(self, *args, **kwargs):
        self.argv_validation('gid', args[0], int)
        cmd = '-g %s' % args[0]
        self.raw_cmds.append(cmd)
        return cmd

    def home(self, *args, **kwargs):
        self.argv_validation('home', args[0], str)
        cmd = '-d %s' % args[0]
        self.raw_cmds.append(cmd)
        return cmd

    def shell(self, *args, **kwargs):
        self.argv_validation('shell', args[0], str)
        cmd = '-s %s' % args[0]
        self.raw_cmds.append(cmd)
        return cmd

    def password(self, *args, **kwargs):
        username = kwargs.get('section')
        password = args[0]
        cmd = 'echo "%s:%s" | sudo chpasswd' % (username, password)
        self.single_line_cmds.append(cmd)

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
        pass


class CentosUser(User):
    def home(self, *args, **kwargs):
        self.argv_validation('home', args[0], str)
        cmd = '-d %s' % args[0]
        return cmd


class WindowsUser(User):
    def home(self, *args, **kwargs):
        print(' in Windows home')