from celery import Celery

############################
# 解决方案 pip install eventlet
# 运行命令：celery -A celery_tasks.main[包名+.main] worker -l info[级别] -P eventlet
############################

# 为celery使用Django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'book_mall.settings.develop'

# 创建celery应用
app = Celery('meiduo')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动注册celery任务
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])



