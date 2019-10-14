# -*- coding: utf-8 -*-
from Arya.backends.base_module import BaseSaltMoude
import os


class State(BaseSaltMoude):

    def apply(self):
        """
        解析任务
        执行任务
        放到任务队列
        返回任务队列id
        :return:
        """
        if '-f' in self.sys_args:
            # yam 配置文件
            yaml_file_index = self.sys_args.index('-f') + 1

            try:
                # 保存配置文件
                yaml_file_name = self.sys_args[yaml_file_index]
                state_data = self.load_state_files(yaml_file_name)

                # 按照不同的操作系统生成不同的配置文件
                for os_type, os_type_data in self.config_data_dic.items():

                    for section_name, section_data in state_data.items():
                        # print(section_name)
                        for mod_name, mod_data in section_data.items():
                            # print('   ', mod_name)  # user.present

                            # 根据配置文件的名字，在plugins中判断是否存在此模块
                            base_mode_name = mod_name.split('.')[0]  # user

                            # 在目录plugin 判断是否有user.py 模块
                            plugin_file_path = '%s/%s.py' % (self.settings.SALT_PLUGINS_DIR, base_mode_name)

                            if os.path.isfile(plugin_file_path):
                                # user.py存在， 则导入模块Arya.plugins.user的包
                                # <module 'Arya' from '/vagrant/Pecah_stack/stack/Arya/__init__.py'>
                                module_plugin = __import__('plugins.%s' % base_mode_name)
                                module_file = getattr(module_plugin, base_mode_name)  # 这里导入相对应的模块

                                # 根据操作系统类型来判断是否在模块下（user）有这个类CentosUser
                                # 操作系统类型的类CentosUser  类型+user
                                special_os_module_name = '%s%s' % (os_type.capitalize(), base_mode_name.capitalize()) # CentosUser
                                print('------> ', special_os_module_name)
                                # Arya.plugins.user里是否存在CentosUser 这个类
                                if hasattr(module_file, special_os_module_name):
                                    # 如果存在，则导入
                                    module_instance = getattr(module_file, special_os_module_name)

                                else:
                                    module_instance = getattr(module_file, base_mode_name.capitalize())

                                module_obj = module_instance(self.sys_args, self.db_models, self.settings)
                                module_obj.syntax_parser(section_name, mod_name, mod_data)

                            else:
                                exit('[ %s ] is not exist' % base_mode_name)

            except IndexError as e:
                exit('state file must -f after')

        else:
            exit('state file must -f after')

