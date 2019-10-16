# -*- coding: utf-8 -*-
from Arya.backends.base_module import BaseSaltMoude


class File(BaseSaltMoude):

    def source(self, *args, **kwargs):
        pass

    def user(self, *args, **kwargs):
        pass

    def group(self, *args, **kwargs):
        pass

    def mode(self, *args, **kwargs):
        pass

    def managed(self, *args, **kwargs):
        return kwargs

    def is_reuqired(self, *args, **kwargs):
        file_path = args[1]
        cmd = 'test -f %s; echo $?' % file_path
        return cmd