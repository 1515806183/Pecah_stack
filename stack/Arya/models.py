from django.db import models

# Create your models here.


class Host(models.Model):
    """
    主机表
    """
    hostname = models.CharField(max_length=128, unique=True, verbose_name='主机名')  # 主机名
    ip = models.CharField(max_length=64, null=True, blank=True, verbose_name='IP')  # ip
    key = models.TextField()  # KEY
    status_choices = (
        (0, '等待批注'),
        (1, '通过批准'),
        (2, '拒绝批准'),
    )

    os_type_choices = (
        ('redhat', 'Redhat'),
        ('centos', 'Centos'),
        ('ubuntu', 'Ubuntu'),
        ('suse', 'Suse'),
        ('windows', 'Windows'),
    )

    status = models.IntegerField(choices=status_choices, verbose_name='批准状态', default=0)  # 批准状态
    os_type = models.CharField(max_length=10 ,choices=os_type_choices, verbose_name='系统类型', default='redhat')  # 系统类型

    def __str__(self):
        return self.hostname

    class Meta:
        db_table = "tb_host"


class HostGroup(models.Model):
    """
    主机组
    """
    name = models.CharField(max_length=64, unique=True, verbose_name='主机组名')  # 组名

    hosts = models.ManyToManyField(Host, blank=True)  # 关联主机

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tb_hostgroup"




