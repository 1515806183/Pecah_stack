# -*- coding: utf-8 -*-
import pika,json


class TaskHandle(object):

    def __init__(self, db_model, task_data, settings, module_obj):
        self.db_model = db_model
        self.task_data = task_data
        self.settings = settings
        self.module_obj = module_obj # 哪个模块调用我，这个变量就是谁 state
        self.make_connection()

    def make_connection(self):
        # 创建MQ的链接
        self.mq_conn = pika.BlockingConnection(pika.ConnectionParameters(
            self.settings.MQ_CONN['host'], port=self.settings.MQ_CONN['port']))
        self.mq_channel = self.mq_conn.channel()  # 打开频道

    def apply_new_task(self):
        '''
        数据库生成一个空数据，返回ID，返回一个任务ID
        :return:
        '''

        new_task_obj = self.db_model.Task()
        new_task_obj.save()
        # 数据库id变成任务id
        self.task_id = new_task_obj.id
        return True

    def dispatch_task(self):
        # 任务格式化和分发
        if self.apply_new_task(): # 数据库ID创建成功
            print('MQ开始发送消息...%s' % self.module_obj.host_list)
            self.callback_queue_name = 'TASK_CALLBACK_%s' % self.task_id  # 设置queue的名字

            data = {
                'data': self.task_data,
                'id': self.task_id,
                'callback_queue': self.callback_queue_name,
                'token': None
            }  # 发给客户端真正数据

            for host in self.module_obj.host_list:
                self.publish(data, host)

            # 消息发送成功，开始等结果
            self.wait_callback()

    def publish(self, data, host):
        """
        # MQ发送任务
        :param data:
        :param host:
        :return:
        """
        # 申明queue
        queue_name = 'TASK_Q_%s' % host.id

        print(' [*] Send task to queue [%s] data %s' % (queue_name, data))
        self.mq_channel.queue_declare(queue=queue_name)  # 设置频道

        self.mq_channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(data))

    def task_callback(ch, method, properties, body):
        print(" [x] Received %r" % (body,))

    def close_connection(self):
        self.mq_conn.close()

    def wait_callback(self):
        """
        等待消息结果
        :return:
        """
        # 申明queue
        self.mq_channel.queue_declare(queue=self.callback_queue_name)

        self.mq_channel.basic_consume(self.task_callback, queue=self.callback_queue_name, no_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')

        self.mq_channel.start_consuming()

