from django.test import TestCase

# Create your tests here.
import re
expr = "'vage' * 100 ".replace(' ', '')  # 'vage'-100

sign = re.findall(r"[\*\+/-]", expr)[-1]  # -


vage_str, num = expr.split(sign)  # ["'vage'", '100']

vage_str = '[1, 2, 3]'

vage = eval(vage_str)

li = "[x %s %s for x in %s]" % (sign, num, vage)

print(eval(li))









