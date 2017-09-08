import io
import boto3
import mimetypes
import os
import zipfile
from botocore.client import Config

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    
    srcBucket = os.environ['srcBucket']
    destBucket = os.environ['destBucket']
    assetsAsZip = os.environ['assetAsZip']
    topicArn = os.environ['topicArn']
    topic = sns.Topic(topicArn)
    
    location = {
        "bucketName": srcBucket,
        "objectKey": assetsAsZip
    }
    
    try:
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]
        
        print("Building Portfolio from " + str(location))
                    
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        destination = s3.Bucket(destBucket)
        source = s3.Bucket(location["bucketName"])
        
        ms = io.BytesIO()
        source.download_fileobj(location["objectKey"], ms)
        
        with zipfile.ZipFile(ms) as myzip:
            for nm in myzip.namelist():
                print (nm)
                obj = myzip.open(nm)
                destination.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                destination.Object(nm).Acl().put(ACL='public-read')
        
        topic.publish(Subject="Portfolio Deployed!", Message="Portfolio deployed successfully!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
        
        print ("Deployment Done!")    
            
    except:
        topic.publish(Subject="Portfolio Deployment Failed!", Message="The Portfolio was not deployed successfully!")
        raise