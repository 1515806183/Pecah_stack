# -*- coding: utf-8 -*-
from modules.base_module import BaseSaltModule
import urllib.request
import os, shutil


class FileModule(BaseSaltModule):

    def func__managed(self, *args, **kwargs):
        module_data = kwargs.get('module_data')
        print('\033[41;1m managed module data:\033[0m', module_data)
        target_filepath = module_data['section']
        if self.has_source:  # 需要把这个文件 copy 成section指定的文件
            if self.source_file is not None:  # 已经下载了
                shutil.copyfile(self.source_file, target_filepath)
                print('copied file from [%s] to [%s]' % (self.source_file, target_filepath))

    def func__user(self,*args,**kwargs):
        pass

    def func__group(self,*args,**kwargs):
        pass

    def func__mode(self,*args,**kwargs):
        pass

    def func__source(self,*args,**kwargs):
        """
        处理下载单个文件
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
        self.has_source = True

    def func__sources(self,*args,**kwargs):
        """
        处理下载多个文件
        :param args:
        :param kwargs:
        :return:
        """
        # 循环下载即可
        for func__source in args[0]:
            self.func__source(func__source)

    def func__require(self,*args,**kwargs):
        """
        依赖处理
        :param args:
        :param kwargs:
        :return:
        """
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
        # task_obj TaskHandle obj, main_obj= Needle obj
        http_server = self.task_obj.main_obj.configs.FILE_SERVER['http']  # 获取服务地址
        # 处理下来文件地址
        url_arg = "file_path=%s" % file_path  # file_path=//apache/httpd.conf
        filename = file_path.split('/')[-1]  # httpd.conf  保存在客户端

        url = "http://%s%s?%s" % (http_server,
                                  self.task_obj.main_obj.configs.FILE_SREVER_BASE_PATH,
                                  url_arg)  # http://192.168.33.10:8000/salt/file_center?file_path=//apache/httpd.conf

        print('\033[45;1mhttpserver\033[0m ', url, self.task_obj.task_body['id'])

        f = urllib.request.urlopen(url)
        data = f.read()

        # /vagrant/Pecah_stack/stack/Arya/Needle/var/downloads/137
        file_save_path = "%s%s" % (self.task_obj.main_obj.configs.FILE_STORE_PATH,
                                    self.task_obj.task_body['id'])
        if not os.path.isdir(file_save_path):
            os.mkdir(file_save_path)

        # 保存文件在本地/var/downloads/137 路径下
        with open("%s/%s" % (file_save_path, filename), "wb") as code:
            code.write(data)

        return "%s/%s" % (file_save_path, filename)












