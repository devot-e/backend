from django.shortcuts import render
from django.http import HttpResponse
from data_generation.models import  File, CSVFile
from django.http import JsonResponse
# from .models import Topic
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework.decorators import api_view
import pandas as pd
import numpy as np
from django.http import JsonResponse
from ctgan import CTGAN
import json
from django.core.exceptions import ObjectDoesNotExist
from table_evaluator import TableEvaluator
import matplotlib
import matplotlib.pyplot as plt
import io
import os
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns


matplotlib.use('Agg')
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# from django.core.files.base import ContentFile
# from django.core.files.storage import FileSystemStorage 

# Create your views here.

@csrf_exempt
@require_POST
def main(request):
    try:
        file= request.FILES['file']
        name=request.POST.get('name')
        print("name = ",name)

        # Specify the directory where you want to save the file
        save_directory = 'data_generation/user_files'

        # Create the directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Use os.path.join to create the full path including the filename
        file_path = os.path.join(save_directory, f"{name}.csv")

        # Save the file with the given name in the specified directory
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        obj= File.objects.create(file = file)
        df= pd.read_csv(obj.file)
        des= df.describe()
        catObj= np.array(df.select_dtypes("object").columns)
        ctgan = CTGAN(verbose=True)
        ctgan.fit(df, catObj, epochs = 2)
        model_path="data_generation/models"

        # Create the directory if it doesn't exist
        if not os.path.exists(model_path):
            os.makedirs(model_path)


        ctgan.save(f"{model_path}/{name}_model.pkl")

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
        model_path = f"data_generation/models/{model_name}_model.pkl"
        
        # Load the pre-trained model
        ctgan = CTGAN.load(model_path)

        samples = ctgan.sample(n_rows)

        generated_path="data_generation/generated_data"

        # Create the directory if it doesn't exist
        if not os.path.exists(generated_path):
            os.makedirs(generated_path)


        samples.to_csv(f"{generated_path}/{model_name}.csv")
        print(samples)
        samples_2d_array = [samples.columns.tolist()] + samples.values.tolist()
        print(samples_2d_array)
        return JsonResponse({'res': samples_2d_array}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Model not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def sample_model(request):
    try:
        data = json.loads(request.body)
        param1= request.query_params.get('model')
        n_rows = int(data.get('n_rows', 10))

        if not param1:
            return JsonResponse({'error': 'model name not provided'}, status= 400)
        # if param1!='adult' or param1!='company':
        #     return JsonResponse({'error': 'Invalid model name'}, status= 400)
        path= f"data_generation/pretrained_models/{param1}.pkl"
        ctgan= CTGAN.load(path)
        samples= ctgan.sample(n_rows)

        generated_path="data_generation/generated_data"

        # Create the directory if it doesn't exist
        if not os.path.exists(generated_path):
            os.makedirs(generated_path)


        samples.to_csv(f"{generated_path}/{param1}.csv")
        samples_2d_array = [samples.columns.tolist()] + samples.values.tolist()

        return JsonResponse({ 'data': samples_2d_array }, status= 200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def generate_report(request):
    try:

        data= json.loads(request.body)
        file_name= data.get('file_name')

        # Construct absolute paths
        file_path = os.path.join(base_dir, "data_generation", "user_files", f"{file_name}.csv")
        new_data_path = os.path.join(base_dir, "data_generation", "generated_data", f"{file_name}.csv")
        # Check if files exist
        if not os.path.exists(file_path) or not os.path.exists(new_data_path):
            return JsonResponse({'error': 'File not found'}, status=404)

        real_data= pd.read_csv(file_path)
        new_data= pd.read_csv(new_data_path)
        generated_data= new_data.drop(new_data.columns[0], axis=1)
        real_stats = real_data.describe()

        table_evaluator = TableEvaluator(real_data,generate_data)

        plot_path="data_generation/plots"

        # Create the directory if it doesn't exist
        if not os.path.exists(plot_path):
            os.makedirs(plot_path)



        pdf_filename=f"{plot_path}/adult.pdf"
        with PdfPages(pdf_filename) as pdf:
            plt.figure(figsize=(10, 6))
            plt.bar(['Real Data', 'Synthetic Data'], [table_evaluator.real_chi2(), table_evaluator.synthetic_chi2()])
            plt.title('Chi-Square Test')
            pdf.savefig()
            plt.close()
        return JsonResponse({'res':'plot created'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)