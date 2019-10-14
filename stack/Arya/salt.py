# -*- coding: utf-8 -*-
import os, sys

if __name__ == "__main__":
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stack.settings")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)

    from Arya.action_list import actions
    from Arya.backends.utils import ArgvManagement
    obj = ArgvManagement(sys.argv)
