import factory
from dvadmin.system.models import FileList


class FileListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FileList

    name = factory.Sequence(lambda n: f"test_file_{n}.txt")
    engine = "rustfs"
    mime_type = "text/plain"
    size = "100"
    md5sum = factory.Faker("md5")
