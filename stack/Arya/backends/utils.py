# -*- coding: utf-8 -*-
import sys, os
from Arya import action_list
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stack.settings")
django.setup()

from Arya import models
from stack import settings


class ArgvManagement(object):
    """
    接受用户指令，分配到对应模块
    """
    def __init__(self, args):
        self.args = args
        self.args_parse()

    def help_msg(self):
        # 打印存在的方法
        print('Avaliable modules:')
        for registe_module in action_list.actions:
            print('   %s' % registe_module)

        exit()

    def args_parse(self):
        """
        解析参数
        python salt.py cmd.run -h 'Centos, Redhat' -g 'group'
        python Arya/salt.py cmd.run -h 'Redhat test,Windows_test' -g 'mail_group'
        :return:
        """
        if len(self.args) < 2:
            self.help_msg()

        module_name = self.args[1]

        if '.' in module_name:
            # cmd.run
            mod_name, mod_method = module_name.split('.')
            module_instance = action_list.actions.get(mod_name)

            if module_instance:  # 如果有，则匹配模块方法成功, 执行方法,传入参数
                module_obj = module_instance(self.args, models, settings)
                module_obj.process()  # 解析配置文件， 提取主机

                if hasattr(module_obj, mod_method):  # 反射取方法
                    mod_method_obj = getattr(module_obj, mod_method)  # 解析任务，发送到队列， 取任务结果
                    mod_method_obj() # 调用指定的方法

                else:
                    exit('   %s 没 [%s] 方法  ' % (mod_name,mod_method))
        else:
            exit('invalid module name argument')








