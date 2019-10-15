# -*- coding: utf-8 -*-
import os, sys
# 客户端主入口

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASE_DIR)
    from core import main
    main.CommandManagement(sys.argv)


