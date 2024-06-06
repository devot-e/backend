from django.shortcuts import render
from django.http import HttpResponse, FileResponse
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
import os
from django.template.loader import get_template
import pandas as pd
from io import BytesIO
from django.template import Context
from os import system
from sdv.metadata import SingleTableMetadata
from sdv.evaluation.single_table import evaluate_quality

# import pdfkit

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
        samples_2d_array = [samples.columns.tolist()] + samples.values.tolist()
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
@require_POST
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

        #getting real and generated data
        real_data= pd.read_csv(file_path)
        new_data= pd.read_csv(new_data_path)
        generated_data= new_data.drop(new_data.columns[0], axis=1)
        
        #extracting sample real and generated data
        real_data_sample= real_data.head()
        generated_data_sample= real_data.head()

        #generating description of real and generated data
        real_stats = real_data.describe()
        generated_stats= generated_data.describe()

        #getting figure from table_evaluator
        table_evaluator = TableEvaluator(real_data,generated_data)
        table_evaluator.visual_evaluation(save_dir=f"data_generation/plots/{file_name}")

        #generating metadata
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(real_data)

        quality_report = evaluate_quality(
            real_data,
            generated_data,
            metadata
        )
        report=quality_report.get_visualization('Column Shapes')
        try:
            # system(f"touch 'data_generation/plots/quality_report.png'")
            file=open(f'data_generation/plots/{file_name}/quality_report.png','ba')
            file.close()
            report.write_image(f'data_generation/plots/{file_name}/quality_report.png',format='png')
        except Exception as e:
            print(e)
        quality_score= str(round(quality_report.get_score()*100, 2))
        data={
            'title': file_name,
            'quality_score': quality_score,
            'quality_report': f'data_generation/plots/{file_name}/quality_report.png',
            'real_data':real_data_sample.to_html(classes='table table-bordered'),
            'real_stats': real_stats.to_html(classes='table table-bordered'),
            'generated_data':generated_data_sample.to_html(classes='table table-bordered'),
            'generated_stats': generated_stats.to_html(classes='table table-bordered'),
            'mean_std_path':f'  data_generation/plots/{file_name}/mean_std.png',
            'cumsums_path':f'data_generation/plots/{file_name}/cumsums.png',
            'distributions_path':f'data_generation/plots/{file_name}/distributions.png',
            'correlation_difference_path': f'data_generation/plots/{file_name}/correlation_difference.png',
            'pca_path': f'data_generation/plots/{file_name}/pca.png',
        }

         # Generate PDF content
        template_src='pdf_template.html'
        
        template = get_template(template_src)
        html = template.render(data)

        generated_path="data_generation/generated_report"

        # Create the directory if it doesn't exist
        if not os.path.exists(generated_path):
            os.makedirs(generated_path)

        with open("x.html",'w') as file:
            file.write(str(html))
        system(f"wkhtmltopdf --enable-local-file-access x.html data_generation/generated_report/{file_name}.pdf")
        generated_pdf_path=f"data_generation/generated_report/{file_name}.pdf"
        pdf_file = open(generated_pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.pdf"'
        return response    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    