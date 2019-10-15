# -*- coding: utf-8 -*-
from conf import configs
import pika
import json,threading


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
        # thread = threading.Thread(target=self.start_thread, args=(body,))
        # thread.start()
