from django.db import models

# class Posting(models.Model):
#     Psnname = models.CharField(max_length=150)
#     image = models.ForeignKey(Image, null=True)


class Image(models.Model):
	Id = models.AutoField(primary_key=True)
	Pname = models.CharField(max_length=500)
	Img = models.ImageField(upload_to="img", null=True, blank=True)

	def __str__(self):
		return self.Pname

# class ImageManager(models.Manager):
# 	def get_image_urls(self):
# 		return 