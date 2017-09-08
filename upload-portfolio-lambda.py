import io
import boto3
import mimetypes
import os
import zipfile
from botocore.client import Config

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        srcBucket = os.environ['srcBucket']
        destBucket = os.environ['destBucket']
        assetsAsZip = os.environ['assetAsZip']
        topicArn = os.environ['topicArn']
        topic = sns.Topic(topicArn)
        
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
        topic.publish(Subject="Portfolio Deployed!", Message="Portfolio deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Deployment Failed!", Message="The Portfolio was not deployed successfully!")
        raise