from django.test import TestCase

# Create your tests here.


a = {'centos':
         [
             {'cmd_list':
                  ['useradd apache -u 87 -g 87 -s /bin/nologin', 'echo "apache:apache" | sudo chpasswd'],
              'require_list':
                  ['more /etc/group | awk -F ":" \'{print $1}\' | grep -w apache -q;echo $?', 'test -f /etc/httpd/conf/httpd.conf; echo &?']},
             {'cmd_list':
                  ['useradd apache -g 87'],
              'require_list':
                  ['more /etc/group | awk -F ":" \'{print $1}\' | grep -w apache -q;echo $?']},


             {'cmd_list':
                  {'section': '/etc/httpd/conf/httpd.conf',
                   'mod_data':
                       [{'source': 'salt://apache/httpd.conf'}, {'user': 'root'}, {'group': 'root'}, {'mode': 644}, {'require': [{'pkg': 'nginx'}]}]},
              'require_list': ['more /etc/group | awk -F ":" \'{print $1}\' | grep -w nginx -q;echo $?'],
              'file_module': True}],


    'redhat': [{'cmd_list':
                    ['useradd apache -u 87 -g 87 -d /var/www/html -s /bin/nologin', 'echo "apache:apache" | sudo chpasswd'],
                'require_list':
                    ['more /etc/group | awk -F ":" \'{print $1}\' | grep -w apache -q;echo $?', 'test -f /etc/httpd/conf/httpd.conf; echo &?']},
               {'cmd_list':
                    ['useradd apache -g 87'],

                'require_list': ['more /etc/group | awk -F ":" \'{print $1}\' | grep -w apache -q;echo $?']},

               {'cmd_list':
                    {'section': '/etc/httpd/conf/httpd.conf',
                     'mod_data': [{'source': 'salt://apache/httpd.conf'}, {'user': 'root'}, {'group': 'root'}, {'mode': 644}, {'require': [{'pkg': 'nginx'}]}]},
                'require_list': ['more /etc/group | awk -F ":" \'{print $1}\' | grep -w nginx -q;echo $?'],

                'file_module': True}]}







b = "'Linux-2.6.32-431.el6.x86_64-x86_64-with-redhat-6.5-Santiago'".split('-')[-3]

print(b)



c = """

{
    'centos': [
        {
            'cmd_list': [
                'useradd apache -u 87 -g 87 -s /bin/nologin',
                 'echo "apache:apache" | sudo chpasswd'
            ],
             'require_list': [
                'more /etc/group | awk -F ":" \'{
                    print $1
                }\' | grep -w apache -q;echo $?',
                 'test -f /etc/httpd/conf/httpd.conf; echo $?'
            ]
        },
         {
            'cmd_list': [
                'groupadd apache -g 87'
            ],
             'require_list': [
                'more /etc/group | awk -F ":" \'{
                    print $1
                }\' | grep -w apache -q;echo $?'
            ]
        },
         {
            'cmd_list': {
                'section': '/etc/httpd/conf/httpd.conf',
                 'mod_data': [
                    {
                        'source': 'http://apache/httpd.conf'
                    },
                     {
                        'user': 'root'
                    },
                     {
                        'group': 'root'
                    },
                     {
                        'mode': 644
                    },
                     {
                        'require': [
                            {
                                'pkg': 'nginx'
                            }
                        ]
                    }
                ]
            },
             'require_list': [
                'more /etc/group | awk -F ":" \'{
                    print $1
                }\' | grep -w nginx -q;echo $?'
            ],
             'file_module': True
        }
    ]
}
"""






