# pylint: disable-msg=C0103

import io
import boto3
import mimetypes
import os
import zipfile
from botocore.client import Config

def lambda_handler(event, context):
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    
    srcBucket = os.environ['srcBucket']
    destBucket = os.environ['destBucket']
    assetsAsZip = os.environ['assetAsZip']
    
    destination = s3.Bucket(destBucket)
    source = s3.Bucket(srcBucket)
    
    ms = io.BytesIO()
    source.download_fileobj(assetsAsZip, ms)
    
    with zipfile.ZipFile(ms) as myzip:
        for nm in myzip.namelist():
            print (nm)
            obj = myzip.open(nm)
            destination.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            destination.Object(nm).Acl().put(ACL='public-read')
    
    print ("Deployment Done!")