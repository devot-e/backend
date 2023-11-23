from django.shortcuts import render
from django.http import HttpResponse
from first_app.models import  File, CSVFile
from django.http import JsonResponse
# from .models import Topic
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import pandas as pd
import numpy as np
from django.http import JsonResponse
from ctgan import CTGAN
import json
from django.core.exceptions import ObjectDoesNotExist


# from django.core.files.base import ContentFile
# from django.core.files.storage import FileSystemStorage 

# Create your views here.

@csrf_exempt
@require_POST
def main(request):
    try:
        file= request.FILES['file']
        obj= File.objects.create(file = file)
        df= pd.read_csv(obj.file)
        name= file.name.split('.')[0]
        des= df.describe()
        catObj= np.array(df.select_dtypes("object").columns)
        ctgan = CTGAN(verbose=True)
        ctgan.fit(df, catObj, epochs = 2)
        ctgan.save(f"first_app/models/{name}_model.pkl")

        # samples = ctgan.sample(10)

        # samples_2d_array = samples.values.tolist()
        # print(samples_2d_array)        
        return JsonResponse(
            {
                'res':'Model trained successfully',
                # 'data': samples_2d_array
            }
        , status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status= 500)


@csrf_exempt
@require_POST
def generate_data(request):
    try:
        data = json.loads(request.body)
        n_rows = int(data.get('n_rows', 10))
        model_name = data.get('model_name')  # Assuming you pass the model name as a parameter
        if not model_name:
            return JsonResponse({'error': 'Model name not provided'}, status=400)
        model_path = f"first_app/models/{model_name}_model.pkl"
        
        # Load the pre-trained model
        ctgan = CTGAN.load(model_path)

        samples = ctgan.sample(n_rows)
        print(samples)
        samples_2d_array = [samples.columns.tolist()] + samples.values.tolist()
        print(samples_2d_array)
        return JsonResponse({'res': samples_2d_array}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Model not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)