# -*- coding: utf-8 -*-
import subprocess

from conf import configs
import pika
import json, threading
import platform
from modules import files


class CommandManagement(object):
    def __init__(self, argvs):
        self.argvs = argvs[1:]  # 取传入的出参数
        self.argv_handler()

    def argv_handler(self):
        if len(self.argvs) == 0:
            exit("argument: start\stop")
        if hasattr(self, self.argvs[0]):
            # 反设执行对应的方法
            func = getattr(self, self.argvs[0])
            func()
        else:
            exit("invalid argument.")

    def start(self):
        client_obj = Needle()
        client_obj.listen()

    def stop(self):
        pass


class Needle():
    def __init__(self):
        self.configs = configs  # 设置全局配置文件
        self.make_connection()
        self.client_id = self.get_needle_id()
        self.task_queue_name = "TASK_Q_%s" % self.client_id  # 拼接自己的任务ID

    def make_connection(self):
        """
        创建MQ的链接
        :return:
        """
        self.mq_conn = pika.BlockingConnection(pika.ConnectionParameters(
            configs.MQ_CONN['host']))

        self.mq_channel = self.mq_conn.channel()

    def get_needle_id(self):
        '''
        去服务器端取自己的id
        :return:
        '''
        return configs.NEEDLE_CLIENT_ID

    def listen(self):
        '''
        开始监听服务器的call
        :return:
        '''
        self.msg_consume()

    def msg_consume(self):
        """
        # 客户端取回服务器消息， 并进行阻塞等待
        :return:
        """

        self.mq_channel.queue_declare(queue=self.task_queue_name)

        self.mq_channel.basic_consume(self.msg_callback,
                                      queue=self.task_queue_name,
                                      no_ack=True)

        print(' [%s] Waiting for messages. To exit press CTRL+C' % self.task_queue_name)
        self.mq_channel.start_consuming()

    def msg_callback(self, ch, method, properties, body):
        """
        打印服务器返回的消息
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        print(" [x] Received a task msg ", body)
        thread = threading.Thread(target=self.start_thread, args=(body,))
        thread.start()

    def start_thread(self, task_body):
        print('\033[31;1m 线程启动开始执行任务 \033[0m')
        task = TaskHandle(self, task_body)
        task.processing()


class TaskHandle(object):
    def __init__(self, main_obj, task_body):
        self.main_obj = main_obj  # 是Needle object
        self.task_body = json.loads(task_body.decode())

    def processing(self):
        check_res = self.check_data_validation()  # 验证tsak数据的合法性
        if check_res:
            self.current_os_type, data = check_res  # ostype, data
            self.parse_task_data(self.current_os_type, data)

    def check_data_validation(self):
        """
        确保服务器发过来的数据在本客户上可以执行
        :return:
        """
        # print('---- 检查数据,确保数据能执行  ----')
        # 取操作系统型号
        os_version = platform.platform().lower().split('-')[-3]

        for os_type, data in self.task_body['data'].items():
            if os_type in os_version:
                return os_type, data
            else:
                print("\033[31;1msalt is not supported on this os \033[0m", os_version)

    def parse_task_data(self, os_type, data):
        """
        解析任务数据并执行
        :param os_type:
        :param data:
        :return:
        """
        applied_list = []  # 所有执行了子任务放在这个列表
        applied_result = []  # 子任务执行完后的结果
        last_loop_section_set_len = len(applied_list)

        while 1:
            for section in data:
                print("\033[31;1m ****************开始解析任务数据********************** \033[0m")
                print("\033[31;1m  \033[0m", section)
                if section.get('called_flag'):  # 如果有代表执行过
                    print('------------------------------called already ')
                else:
                    apply_status, result = self.apply_section(section)
                    # 表示命令执行成功
                    if apply_status:
                        # 把执行过的命令和结果保存
                        applied_list.append(section)
                        applied_result += result

            if len(applied_list) == last_loop_section_set_len:
                # 这两个变量相等, 代表2种可能, 要么是都执行完了, 要么是依赖关系形成了死锁
                break

            last_loop_section_set_len = len(applied_list)

        # 接下来把执行结果返回给服务器
        print('\033[42;1msend task result to task callback queue:\033[0m', self.task_body['callback_queue'])
        self.task_callback(self.task_body['callback_queue'], applied_result)

    def apply_section(self, section_data):
        """
        执行指定的task section
        :param section_data:
        :return:
        """
        print("\033[32;1m 开始判断require_list依赖是否满足\033[0m".center(50, '-'))
        if section_data.get('require_list') != None:
            # 检测requsite条件是否满足
            if self.check_pre_requisites(section_data.get('require_list')) == 0:
                print("\033[33;1m ****************require_list依赖 满足**********************\033[0m")
                if section_data.get('file_module'):  # 单独处理文件
                    res = self.file_handle(section_data)
                else:
                    res = self.run_cmds(section_data.get('cmd_list'))
                section_data['called_flag'] = True
                return [True, res]
            else:
                print("\033[33;1m ****************require_list依赖不满足**********************\033[0m")
                return [False, None]  # 依赖不满足

        else: # 没依赖要求,直接执行
            if section_data.get('file_module') == True: #文件section需要单独处理
                res = self.file_handle(section_data)
            else:
                res = self.run_cmds(section_data['cmd_list'])

            section_data['called_flag'] = True
            return [True,res]

    def check_pre_requisites(self, require_list):
        """
        检测依赖条件是否成立
        :param require_list:
        :return:
        """
        # print('---- 检查依赖环境 require_list 是否成立 ----')
        condition_results = []
        for condition in require_list:
            # 单独开启进程执行命令
            print(condition)
            cmd_res = subprocess.run(condition, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            condition_results.append(int(cmd_res.stdout.decode().strip()))  # 返回的bytes类型,必须转换
        print(condition_results)
        return sum(condition_results)  # 所有命令执行成功的话就是 0

    def file_handle(self, section_data):
        """
        对文件进行操作,服务器返回的未处理文件数据
        :param section_data:
        :return:
        """
        print('---- 对文件进行操作  是否成立 ----')
        file_module_obj = files.FileModule(self)
        file_module_obj.process(section_data)
        return []

    def run_cmds(self, cmd_list):
        """
        运行命令,返回结果
        :param cmd_list:
        :return:
        """
        print('---- 运行命令,返回结果 ----')
        cmd_results = []
        for cmd in cmd_list:
            print(cmd)
            cmd_res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cmd_results.append([cmd_res.returncode, cmd_res.stderr.decode()])  # 3.5以前
            # cmd_res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #
            # cmd_results.append(int(cmd_res.stdout.decode().strip()))
        print('\033[41;1m执行结果:\033[0m', cmd_results)
        return cmd_results  # 所有命令如果执行成功,返回是0

    def task_callback(self, callback_queue, callback_data):
        """
        把任务执行结果返回给服务器
        :param callback_queue:
        :param applied_result:
        :return:
        """
        data = {
            'client_id': self.main_obj.client_id,  # Needle
            'data': callback_data
        }

        #声明queue  TASK_CALLBACK_137
        self.main_obj.mq_channel.queue_declare(queue=callback_queue)
        self.main_obj.mq_channel.basic_publish(exchange='',
                                               routing_key=callback_queue,
                                               body=json.dumps(data))

        print(" [x] Sent task callback to [%s]" % callback_queue)


