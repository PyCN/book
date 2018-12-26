from .yuntongxun.sms import CCP
from celery_tasks.main import app
import logging
logger = logging.getLogger('django')


# 使用装饰器进行任务添加
@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, expires, temp_id):
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, expires], temp_id)
    except Exception as e:
        logging.error('短信发送[异常]，手机号：%s,error_message:%s' % (mobile, e))
    else:
        if result == 0:
            logger.info('短信发送[成功]，手机号：%s' % mobile)
        else:
            logger.warning('短信发送【失败】手机号：%s' % mobile)
