import factory
import factory.django
from apps.pisadmin.basicinfo.models import Currency, Unit


class CurrencyFactory(factory.django.DjangoModelFactory):
    """
    Currency 模型测试数据工厂

    注意: 模型字段名为 'factory'，与 factory_boy 模块名冲突，
    故使用 model= (非 factory=) 并通过 LazyAttribute 赋值。
    """

    class Meta:
        model = Currency
        # 用 model= 而非 factory= 避免 factory 模块名冲突

    currencyname = factory.Faker("currency_name")
    currencycode = factory.Faker("currency_code")
    currencysymbol = factory.Faker("currency_symbol")
    # 模型字段 factory 有 null=True，故此处直接赋值为 None
    tax = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    status = 1


class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Unit

    unitname = factory.Faker("word")
    unitcode = factory.Faker("random_element", elements=["PC", "KG", "BOX", "SET"])
    status = 1
