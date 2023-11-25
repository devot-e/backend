from django.db import models

# Create your models here.

# class Topic(models.Model):
#     top_name= models.CharField(max_length=264, unique= True)

#     def __str__(self):
#         return self.top_name
    
# class Webpage(models.Model):
#     topic= models.ForeignKey(Topic, on_delete=models.DO_NOTHING)
#     name=  models.CharField(max_length=264, unique=True)
#     url= models.URLField(unique=True)

#     def __str__(self):
#         return self.name
    
# class AccessRecord(models.Model):
#     name= models.ForeignKey(Webpage, on_delete=models.DO_NOTHING)
#     date= models.DateField()

#     def __str__(self):
#         return str(self.date)

class File(models.Model):
    file= models.FileField(upload_to="files")

class CSVFile(models.Model):
    # file_name= models.FilePathField()
    mean= models.CharField(max_length=1000)
    std= models.CharField(max_length=1000)
    min= models.CharField(max_length=1000)
    max= models.CharField(max_length=1000)
    # columns= ArrayField(models.CharField(max_length=1000))