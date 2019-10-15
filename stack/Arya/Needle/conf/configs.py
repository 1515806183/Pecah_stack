# -*- coding: utf-8 -*-
# 客户端配置文件

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SALT_MASTER = '192.168.33.10'

NEEDLE_CLIENT_ID = 1

# MQ 配置
MQ_CONN = {
    'host':'192.168.33.10',
    'port': 5672,
    'password': 'admin'
}