# pylint: disable-msg=C0103

import io
import zipfile
import boto3
from botocore.client import Config
import mimetypes

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

PORTFOLIO_BUCKET = 'portfolio.toddghetrick.info'
BUILD_BUCKET = 'buildit.toddghetrick.info'

myportfolio = s3.Bucket(PORTFOLIO_BUCKET)
mybuild = s3.Bucket(BUILD_BUCKET)

ms = io.BytesIO()
mybuild.download_fileobj('portfoliobuild/artifacts.zip', ms)

with zipfile.ZipFile(ms) as myzip:
    for nm in myzip.namelist():
        print (nm)
        obj = myzip.open(nm)
        myportfolio.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
        myportfolio.Object(nm).Acl().put(ACL='public-read')