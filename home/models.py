from django.db import models


class ContactUs(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False)
    email = models.CharField(max_length=50, null=False, blank=False)
    message = models.CharField(max_length=254, null=False, blank=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)