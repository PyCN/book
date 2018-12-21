from datetime import datetime
from django.db import models


class BaseModel(models.Model):
    """基础模型类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 说明是抽象模型类，用户继承使用，数据库迁移时不会创建BaseModel的表
        abstract = True



