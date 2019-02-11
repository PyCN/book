from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from book_mall.utils.models import BaseModel


class Category(BaseModel):
    """
    商品类别
    """
    name = models.CharField(max_length=100, verbose_name='名称')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父类别')

    class Meta:
        db_table = 'tb_book_category'
        verbose_name = '图书类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Channel(BaseModel):
    """
    图书频道
    """
    group_id = models.IntegerField(verbose_name='组号')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='顶级商品类别')
    url = models.CharField(max_length=50, verbose_name='频道页面链接')
    sequence = models.IntegerField(verbose_name='组内顺序')

    class Meta:
        db_table = 'tb_book_channel'
        verbose_name = '图书频道'
        verbose_name_plural = verbose_name
        ordering = ['group_id', 'sequence']

    def __str__(self):
        return self.category.name


class SKU(BaseModel):
    """
    图书
    """
    name = models.CharField(max_length=100, verbose_name='名称')
    author = models.CharField(max_length=100, verbose_name='作者', default='')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='从属类别')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='进价')
    market_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='市场价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    desc_detail = RichTextUploadingField(default='', verbose_name='详细介绍')
    desc_service = RichTextUploadingField(default='', verbose_name='售后服务')
    is_launched = models.BooleanField(default=True, verbose_name='是否上架销售')
    default_image_url = models.CharField(max_length=200, default='', null=True, blank=True, verbose_name='默认图片')

    class Meta:
        db_table = 'tb_book'
        verbose_name = '图书'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s > %s' % (self.id, self.name)


class SKUImage(BaseModel):
    """
    SKU图片
    """
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='图书')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_book_image'
        verbose_name = '图书图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s > %s' % (self.sku.name, self.id)


class AdvertiseCategory(BaseModel):
    """
    图书广告类别
    """
    name = models.CharField(max_length=100, verbose_name='名称')

    class Meta:
        db_table = 'tb_advertise_category'
        verbose_name = '图书广告类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Advertise(BaseModel):
    """
    图书广告
    """
    category = models.ForeignKey(AdvertiseCategory, on_delete=models.CASCADE, verbose_name='图书广告分类', default='', related_name='advertise')
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='图书')

    class Meta:
        db_table = 'tb_advertise'
        verbose_name = '图书广告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name


class KeyWord(BaseModel):
    """
    图书关键字搜索
    """
    name = models.CharField(max_length=10, verbose_name="名称")

    class Meta:
        db_table = 'tb_keyword'
        verbose_name = '图书关键字'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name