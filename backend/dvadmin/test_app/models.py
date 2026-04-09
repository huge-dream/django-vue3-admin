from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    author = models.CharField(max_length=100, verbose_name="作者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "test_blog"
        verbose_name = "博客"
        verbose_name_plural = verbose_name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="产品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    stock = models.IntegerField(verbose_name="库存")
    category = models.CharField(max_length=100, verbose_name="分类")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "test_product"
        verbose_name = "产品"
        verbose_name_plural = verbose_name
