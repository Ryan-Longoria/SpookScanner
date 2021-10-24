from google.cloud import storage
from PIL import Image, ImageFilter
from time import time

TMP = "/tmp/"

def resize(image, file_name):
    path = TMP + "resized-" + file_name
    image.thumbnail((128, 128))
    image.save(path)
    return [path]

def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += resize(image, file_name)

    latency = time() - start
    return latency, path_list

def list_blobs(bucket):
    blobs = bucket.list_blobs()
    for blob in blobs:
        print(blob.name)
        return blob.name
        
def download_blob(blob, download_path):
    blob.download_to_filename(download_path)
    print('Blob {} downloaded to {}.'.format(
        blob.name,
        download_path))

def upload_blob(bucket_name, blob, upload_path):
    blob.upload_from_filename(upload_path)
    print('File {} uploaded to {}.'.format(
        blob.name,
        bucket_name))
    
FILE_NAME_INDEX = 2

def function_handler(request):
    request_json = request.get_json(silent=True)
    bucket_name = request_json['bucket']
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    print("bucket:",bucket)
    
    blob_name = list_blobs(bucket)
    blob = bucket.blob(blob_name)
    
    download_path = "/tmp/" + blob_name
    download_blob(blob, download_path)
    
    latency, path_list = image_processing(blob_name, download_path) 
    
    for upload_path in path_list:
        file_name = upload_path.split("/")[FILE_NAME_INDEX]
        u_blob = bucket.blob(file_name)
        upload_blob(bucket_name, u_blob, upload_path) 
    
    
    return "latency : " + str(latency)