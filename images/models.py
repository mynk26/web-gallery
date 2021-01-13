from django.db import models
from picklefield.fields import PickledObjectField
from account.models import user_account
from django.utils import timezone
def get_img_add(instance,filename):
    return 'media/ImageData/{0}/All/{1}'.format(instance.user.username,filename)
def get_thumb_add(instance,filename):
    return 'media/ImageData/{0}/thumb/{1}'.format(instance.user.username, filename)
# Create your models here.
class Links(models.Model):
    user = models.OneToOneField(user_account, on_delete=models.CASCADE, primary_key=True)
    link = PickledObjectField()

class Images(models.Model):
    user = models.ForeignKey(user_account, on_delete=models.CASCADE)
    height = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    image = models.ImageField(upload_to=get_img_add, height_field='height', width_field='width')
    thumb = models.ImageField(upload_to=get_thumb_add)
    last_seen=models.DateField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    like = models.BooleanField(default=False)