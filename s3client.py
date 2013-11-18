from boto.s3.connection import S3Connection
from boto.s3.key import Key

#'AKIAJ2MGY2Q7VXL3LUOA','g1qsMjzhQvwagkut6rRyYY6Uf1SJx9ZhksrPwFCU'

class S3Client(object):

    def __init__(self,key,secret,bucket):
        self.conn = S3Connection(key,secret)
        self.b = self.conn.get_bucket(bucket)

    def upload(self,filename):
        self.upload_file(file)

    def upload_file(self,file):
        k = Key(self.b)
        k.key=file.name
        k.set_contents_from_file(file)
        k.compute_md5(file)

    def close(self):
        self.conn.close()
