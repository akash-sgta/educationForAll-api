from django.db import models

import os

## ============================================================================= ##


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    ext = models.CharField(max_length=15, blank=True, null=True)
    data = models.ImageField(upload_to="upload/image/%Y/%m/%d/")

    def save(self, *args, **kwargs):
        self.ext = self.data.name.split(".")[-1]

        return super(Image, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.data.path):
            os.remove(self.data.path)

        return super(Image, self).delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        if os.path.isfile(self.data.path):
            os.remove(self.data.path)

        if super(Image, self).delete(*args, **kwargs):
            self.ext = self.data.name.split(".")[-1]
            return super(Image, self).save(*args, **kwargs)
        else:
            raise ValueError("Unsuccessful Update")

    def __str__(self):
        return f"{self.id} | {self.data.name}"


class File(models.Model):
    id = models.AutoField(primary_key=True)
    ext = models.CharField(max_length=15, blank=True, null=True)
    data = models.FileField(upload_to="upload/file/%Y/%m/%d/")

    def save(self, *args, **kwargs):
        self.ext = self.data.name.split(".")[-1].upper()

        return super(Image, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.data.path):
            os.remove(self.data.path)

        return super(Image, self).delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        if os.path.isfile(self.data.path):
            os.remove(self.data.path)

        if super(Image, self).delete(*args, **kwargs):
            self.ext = self.data.name.split(".")[-1].upper()
            return super(File, self).save(*args, **kwargs)
        else:
            raise ValueError("Unsuccessful Update")

    def __str__(self):
        return f"{self.id} | {self.data.name}"
