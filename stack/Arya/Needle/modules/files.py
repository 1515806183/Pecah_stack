# -*- coding: utf-8 -*-
from modules.base_module import BaseSaltModule


class FileModule(BaseSaltModule):

    def func__user(self,*args,**kwargs):
        pass

    def func__group(self,*args,**kwargs):
        pass

    def func__mode(self,*args,**kwargs):
        pass

    def func__source(self,*args,**kwargs):
        """
        处理下载文件
        :param args:
        :param kwargs:
        :return:
        """
        fileurl = args[0] # 文件路径
        print('downloading ...', fileurl)
        download_type, file_path = fileurl.split(":")  # 下载格式 salt://apache/httpd.conf
        # 反射 生成多个下载文件方式 http salt
        file_download_func = getattr(self, 'download_%s' % download_type)
        self.source_file = file_download_func(file_path)

    def func__require(self,*args,**kwargs):
        pass

    def download_salt(self, file_path):
        """
        salt 下载文件方式
        :param file_path:
        :return:
        """
        print('donlowding from salt:', file_path)

    def download_http(self, file_path):
        """
        http 下载文件方式
        ("downloading with urllib2")
        :param file_path:
        :return:
        """
        print('donlowding from http:', file_path)
        # task_obj TaskHandle obj, main_obj= Needle obj
        http_server = self.task_obj.main_obj.configs.FILE_SERVER['http']  # 获取服务地址
        # 处理下来文件地址
        url_arg = "file_path=%s" % file_path  # file_path=//apache/httpd.conf
        filename = file_path.split('/')[-1]  # httpd.conf

        url = "http://%s%s?%s" % (http_server,
                                  self.task_obj.main_obj.configs.FILE_SREVER_BASE_PATH,
                                  url_arg)  # http://192.168.33.10:8000/salt/file_center?file_path=//apache/httpd.conf




