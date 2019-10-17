# -*- coding: utf-8 -*-
import os
from yaml import load, dump


class BaseSaltMoude(object):
    """
    处理主机类型公共类
    """

    def __init__(self, sys_args, db_models, settings):
        self.sys_args = sys_args
        print('***************************', sys_args)
        self.db_models = db_models
        self.settings = settings
        self.host_list = []

    def get_module_instance(self, *args, **kwargs):
        # 在目录plugin 判断是否有user.py 模块
        base_mode_name = kwargs.get('base_mode_name')
        os_type = kwargs.get('os_type')

        plugin_file_path = '%s/%s.py' % (self.settings.SALT_PLUGINS_DIR, base_mode_name)
        if os.path.isfile(plugin_file_path):
            # user.py存在， 则导入模块Arya.plugins.user的包
            # <module 'Arya' from '/vagrant/Pecah_stack/stack/Arya/__init__.py'>
            module_plugin = __import__('plugins.%s' % base_mode_name)
            module_file = getattr(module_plugin, base_mode_name)  # 这里导入相对应的模块

            # 根据操作系统类型来判断是否在模块下（user）有这个类CentosUser
            # 操作系统类型的类CentosUser  类型+user
            special_os_module_name = '%s%s' % (os_type.capitalize(), base_mode_name.capitalize())  # CentosUser
            print('\033[0;41m------> %s: \033[0m' % special_os_module_name)

            # Arya.plugins.user里是否存在CentosUser 这个类
            if hasattr(module_file, special_os_module_name):
                # 如果存在，则导入
                module_instance = getattr(module_file, special_os_module_name)

            else:
                module_instance = getattr(module_file, base_mode_name.capitalize())

            module_obj = module_instance(self.sys_args, self.db_models, self.settings)
            return module_obj

        else:
            exit('[ %s ] is not exist' % base_mode_name)

    def process(self):
        self.fetch_hosts()
        self.config_data_dic = self.get_os_type_and_ip()

    def is_reuqired(self, *args, **kwargs):
        exit('Error: [ %s ] is not reuqired..' % args[0])

    def require(self, *args, **kwargs):
        """
        全局，所有模块都可以用，
        检测依赖,
        :param args:
        :param kwargs:
        :return:
        """
        os_type = kwargs.get('os_type')
        self.require_list = []

        for item in args[0]:
            for mod_name, mod_val in item.items():
                mod_obj = self.get_module_instance(base_mode_name=mod_name, os_type=os_type)
                require_condition = mod_obj.is_reuqired(mod_name, mod_val)
                self.require_list.append(require_condition)

        print('\033[0;41mrequire_list: \033[0m', self.require_list)

    def get_os_type_and_ip(self):
        """
        data = {
            0: [],
            1: []
        }
        :return: 提取主机系统和主机IP
        """
        data = {}

        for host in self.host_list:
            data[host.os_type] = []
        print('   data--->', data)
        return data

    def fetch_hosts(self):
        print('提取主机'.center(80, '-'), ' ')
        host_list = []
        if '-h' in self.sys_args or '-g' in self.sys_args:
            if '-h' in self.sys_args:
                # 根据主机名提取
                host_str_index = self.sys_args.index('-h') + 1

                if len(self.sys_args) <= host_str_index:
                    exit('host 必须在 -h 之后')
                else:
                    host_str = self.sys_args[host_str_index]
                    host_str_list = host_str.split(',')
                    host_list += self.db_models.Host.objects.filter(hostname__in=host_str_list)
            if '-g' in self.sys_args:
                # 主机组提取主机
                group_str_index = self.sys_args.index('-g') + 1

                if len(self.sys_args) <= group_str_index:
                    exit('group 必须在 -g 之后')
                else:
                    group_str = self.sys_args[group_str_index]
                    host_str_list = group_str.split(',')
                    group_list = self.db_models.HostGroup.objects.filter(name__in=host_str_list) # 取到的是主机组

                    # 提取主机组下面的主机
                    # ORM select_related适用于外键和多对一的关系查询
                    # prefetch_related适用于一对多或者多对多的查询
                    for group in group_list:
                        host_list += group.hosts.select_related()

            self.host_list = set(host_list)
            print('   host_list:---->', self.host_list)
            return True
        else:
            exit('host [-h] or group [-g] must be provided')

    def load_state_files(self, state_filename):
        """
        解析 拆分yaml 文件
        :param state_filename:
        :return:
        """
        try:
            from yaml import CLoader as Loader, CDumper as Dumper
        except ImportError:
            from yaml import Loader, Dumper

        yaml_file_path = "%s/%s" % (self.settings.SALT_CONFIG_FILES_DIR, state_filename)
        if os.path.isfile(yaml_file_path):
            with open(yaml_file_path) as f:
                data = load(f.read(), Loader=Loader)
            return data

        else:
            exit(   '%s not config file' % state_filename)

    def syntax_parser(self, section_name, mod_name, mod_data, os_type):
        """
        语法检查
        :return:
        """
        print('->',section_name)
        print('   ', mod_name)
        print('      ', mod_data)
        self.raw_cmds = []
        self.single_line_cmds = []

        for data_item in mod_data:
            for key, val in data_item.items():
                if hasattr(self, key):
                    state_func = getattr(self, key)
                    state_func(val, section=section_name, os_type=os_type)
                else:
                    exit(' [ %s ] 没有 [ %s ] 这个方法.' % (mod_name, key))
        else:
            if '.' in mod_name:
                # 校验 user.present 是否存在 present
                base_mode_name, mod_action = mod_name.split('.')
                if hasattr(self, mod_action):
                    mod_action_func = getattr(self, mod_action)
                    # 拼接命令
                    cmd_list = mod_action_func(section=section_name, mod_data=mod_data) # present
                    # present 这里mod_data 是flie模块使用， 把数据交给客户端处理
                    data = {
                        'cmd_list': cmd_list,
                        'require_list': self.require_list
                    }

                    if type(cmd_list) is dict:
                        data['file_module'] = True
                        data['sub_action'] = cmd_list.get('sub_action')

                    # 上面代表一个section里面具体的一个module结束了
                    return data

                else:
                    exit(' [ %s ] 没有方法 [ %s ]' % (mod_name, mod_action))

            else:
                exit('[ %s ] 后面必须有动作' % (mod_name))

    def argv_validation(self, argv_name, val, data_type):
        """
        检查参数合法性
        :param val:
        :param data_type:
        :return:
        """
        if type(val) is not data_type:
            exit('%s 参数类型错误' % argv_name)



