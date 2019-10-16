# -*- coding: utf-8 -*-


class BaseSaltModule(object):
    def __init__(self,task_obj):
        self.task_obj = task_obj  # TaskHandle 对象

    def process(self, module_data, *args, **kwargs):
        print("file mod".center(60, '='))
        print(module_data)
        section_name = module_data['cmd_list']['section']  # /etc/httpd/conf/httpd.conf
        section_data = module_data['cmd_list']['mod_data'] # list [{'source': 'salt://apache/httpd.conf'}, {'user': 'root'}, {'group': 'root'}, {'mode': 644}, {'require': [{'pkg': 'nginx'}]}]
        sub_action = module_data['cmd_list'].get('sub_action')  # file.managed: 中的managed

        for mod_item in section_data:
            # 遍历反射取对应的模块
            for k, v in mod_item.items():
                state_func = getattr(self, 'func__%s' % k)
                state_func(v)

        if sub_action: #如果有,就执行,基本只针对 文件 模块
            sub_action_func = getattr(self,'func__%s' % sub_action)
            sub_action_func(module_data=module_data['raw_cmds'])