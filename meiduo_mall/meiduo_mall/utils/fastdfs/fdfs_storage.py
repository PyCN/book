from fdfs_client.client import Fdfs_client
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class FastDFSStorage(Storage):
    """
    自定义文件存储系统，实现将文件保存到FastDFS服务器上
    """
    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url: 用于构造图片完整路径使用，图片服务器的域名
        :param client_conf: FastDFS客户端配置文件的路径 FastDFS客户端配置文件的路径
        """
        self.base_url = base_url or settings.FDFS_URL
        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF

    def _open(self, name, mode='rb'):
        """在FastDFS中打开文件"""
        pass

    def _save(self, name, content, max_length=None):
        """
        在FastDFS中保存文件
        :param name: 传入的文件名
        :param content: 文件对象
        :return: 保存到数据库中的FastDFS的文件名
        """
        client = Fdfs_client(self.client_conf)
        ret = client.upload_by_buffer(content.read())

        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")

        file_name = ret.get("Remote file_id")
        return file_name

    def url(self, name):
        """
        返回完整的url路径
        :param name: 数据库中文件的名字
        :return: 完整的url路径
        """
        return self.base_url + name

    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件的重名问题
        所以此处返回False，告诉Django上传的都是新文件
        :param name: 文件名
        :return: false
        """
        return False
