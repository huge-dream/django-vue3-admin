import factory
from dvadmin.system.models import Users


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Users

    username = factory.Sequence(lambda n: f"user_{n}")
    password = factory.Faker("password", length=12)
    is_active = True
    is_superuser = False

    class Params:
        admin = factory.Trait(is_superuser=True)
