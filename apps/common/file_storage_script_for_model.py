from django.utils import timezone


class UploadPath:
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        date = timezone.now()

        return f"{self.folder}/{date:%Y/%m/%d/%H/%M}/{filename}"

    def deconstruct(self):
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}",
            [self.folder],
            {},
        )