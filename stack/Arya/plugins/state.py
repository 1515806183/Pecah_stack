# -*- coding: utf-8 -*-
from Arya.backends.base_module import BaseSaltMoude
import os
from Arya.backends import tasks

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

                            module_obj = self.get_module_instance(base_mode_name=base_mode_name, os_type=os_type)
                            moudle_parse_result = module_obj.syntax_parser(section_name, mod_name, mod_data, os_type)
                            self.config_data_dic[os_type].append(moudle_parse_result)

                print('config_data_dic'.center(60, '*'))
                print(self.config_data_dic)

                # 生成任务mq消息
                new_task_obj = tasks.TaskHandle(self.db_models,self.config_data_dic,self.settings,self)
                new_task_obj.dispatch_task() # 分发任务

            except IndexError as e:
                exit('state file must -f after')

        else:
            exit('state file must -f after')

