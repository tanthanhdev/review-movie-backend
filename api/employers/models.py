from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from s3direct.fields import S3DirectField
from django.db import transaction
import uuid
from django.utils.text import slugify 
from django.utils.crypto import get_random_string
from django.core.validators import validate_image_file_extension
from django.db.models.signals import post_save
from django.dispatch import receiver
# Models
from api.users.models import User

# Create your models here.
def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

# Table Employers
def employer_upload_file(instance,filename):
    id = str(instance).split('-')[0]
    return "employer/{id}/images/{filename}".format(filename=filename, id=id)
    # return "account/employer/images/{random}_{filename}".format(filename=filename, random=get_random_string(4)) 
class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    #
    company_name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    company_location = models.CharField(max_length=255, null=True, blank=True)
    company_size = models.BigIntegerField(null=True, blank=True)
    # logo = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to=employer_upload_file, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    web_link = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False, null=True, blank=True) #True: dang tuyen dung, Flase: khong tuyen dung
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('pk',)
        db_table = 'employers'
    
    def __str__(self):
        return str(self.pk) + "-" + self.user.email
    
    def employer_user_email(self):
        try:
            return self.user.email
        except:
            return None
    
    def delete(self, using=None, keep_parents=False):
        # try:
        #     self.image.storage.delete(self.image.name)
        # except: pass
        try:
            self.image.delete()
        except: pass
        super().delete()  
        
    def save(self, *args, **kwargs):
        # slug save
        self.slug = unique_slugify(self, slugify(self.company_name))
        # ========================
        super(Employer, self).save(*args, **kwargs)

# Table Company files
def company_file_upload_file(instance,filename):
    return "employer/{instance}/images/{filename}".format(filename=filename, instance=instance)
    # return "account/employer/images/{random}_{filename}".format(filename=filename, random=get_random_string(4)) 
class CompanyFile(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #
    image = models.ImageField(upload_to=company_file_upload_file, null=True, blank=True)
    video = models.ImageField(upload_to=company_file_upload_file, null=True, blank=True)
    # image = models.CharField(max_length=255, null=True, blank=True)
    # video = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.employer.pk)

    class Meta:
        ordering = ('-pk',)
        db_table = 'company_files'
    
    def delete(self, using=None, keep_parents=False):
        # try:
        #     self.image.storage.delete(self.image.name)
        # except: pass
        try:
            self.image.delete()
            self.video.delete()
        except: pass
        super().delete()  