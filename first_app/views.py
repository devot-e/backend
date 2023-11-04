from django.shortcuts import render
from django.http import HttpResponse
from first_app.models import  File, CSVFile
from django.http import JsonResponse
# from .models import Topic
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
from django.http import JsonResponse
from ctgan import CTGAN

# from django.core.files.base import ContentFile
# from django.core.files.storage import FileSystemStorage 

# Create your views here.

@csrf_exempt
def main(request):
    if request.method=='POST':
        file= request.FILES['file']
        obj= File.objects.create(file = file)
        df= pd.read_csv(obj.file)
        name= file.name.split('.')[0]
        # print(np.array(df)[0])
        des= df.describe()
        serial_mean= des.loc['mean'].to_dict()
        serial_std= des.loc['std'].to_dict()
        serial_min= des.loc['min'].to_dict()
        serial_max= des.loc['max'].to_dict()
        #generate data
        catObj= np.array(df.select_dtypes("object").columns)
        ctgan = CTGAN(verbose=True)
        ctgan.fit(df, catObj, epochs = 2, embedding_dim= 200)
        ctgan.save(f"first_app/models/{name}_model.pkl")

        samples = ctgan.sample(1000)
        print(samples.head())
        
        return JsonResponse(
            {
            'serial_mean': serial_mean,
            'serial_std': serial_std,
            'serial_max': serial_max,
             'serial_min':serial_min,

        }
        # obj
        , status=200)
    

