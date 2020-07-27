from django.db import models


class AppKey(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False, verbose_name=u'名字')
    project_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'项目名字')
    project_key = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'项目key')
    access_key = models.CharField(max_length=255, null=False, blank=False, verbose_name=u'access_key')
    secret_key = models.CharField(max_length=255, null=False, blank=False, verbose_name=u'secret_key')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    remark = models.CharField(max_length=100, null=True, blank=True, default='', verbose_name=u'备注')

    class Meta:
        ordering = ('-create_time',)

    def __unicode__(self):
        return self.name

