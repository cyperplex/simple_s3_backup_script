__author__ = "Owen Corcoran"
__copyright__ = "Copyright 2019"
__version__ = "0.0.2"
__maintainer__ = "Owen Corcoran"
__email__ = "cyperplex@gmail.com"
__information__ = "Simple script to backup files to S3 using IAM, S3 Bucket. This will require the presence of an IAM account, S3 bucket with associated access policy and role assigned to the iam user to write data"

import json, boto3, logging, time, os, glob, zipfile
from botocore.exceptions import ClientError

config_dictionary = {}

def zip_directories(path, ziph):
    '''
    :param path: Path to create the archive from
    :param ziph: ZIP Algorithm
    :return:
    '''
    # ziph is zipfile handle
    try:
        for root, dirs, files in os.walk(path):
            total_file_number = len(files)
            file_count = total_file_number
            print("Opening following path", path)
            for file in files:
                ziph.write(os.path.join(root, file))
                print(file_count, " of files processed out of ", total_file_number)
                file_count = (file_count - 1)
    except OSError as error:
        print(error)
def read_json_config(filename):
    '''
    Function to read the json config file provided with aws creds and remote bucket name
    :param filename:  Config file name
    :return: config dictionary for parsing into credential key:value elements for boto3 request
    '''
    with open(filename) as json_data_file:
        config_dictionary = json.load(json_data_file)
        return config_dictionary
def upload_s3(config_dictionary, file, bucket_suffix):
    '''
    :param config_dictionary: directory where the configuration file is located for reading
    :param path: provided local path for backup
    :param bucket_suffix: suffix name  for the backup folder which is appended after date, to describe the files being backed up
    :return: return false or true depending on success
    '''
    print("Hello ", os.getlogin(), ", lets backup")
    try:
        print("Upload file to Amazon S3")
        print("Processing file", file)
        s3_client = boto3.resource(
            's3',
            aws_access_key_id=config_dictionary['s3']['access-key'],
            aws_secret_access_key=config_dictionary['s3']['secret-access-key']
        )
        try:
            tdate = time.strftime("%Y.%m.%d")
            fullfoldername = tdate + "_" + bucket_suffix + "/"
            s3_client.meta.client.upload_file(file, config_dictionary['s3']['bucket'], fullfoldername + file)
        except Exception  as ex:
            print("exception error" , ex)
            print("Unable to make S3 upload request for ", file)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def create_archive(pathname):
    tdate = time.strftime("%Y.%m.%d")
    zip_file_name = 'archive_'+tdate+'.zip'
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zip_directories(path_1_listing, zipf)
    print("Writing Archive: ", zip_file_name)
    zipf.close()
    print("Archive Write Completed: ", zip_file_name)
    try:
        print("Attempting to upload archive to AWS S3")
        upload_s3(configuration,zip_file_name, "remotefoldername")
    except:
        print("Unable to upload to S3")
        return 1
if __name__ == '__main__':
   # Main INIT function, reads in configuration to authentication to aws and also should be provied with a list of paths to be archived
   
    configuration = read_json_config('config.json')
    print("Loading Configuration", json.dumps(configuration, indent=4))
    try:
        path_1_listing = 'c:\\tester'
        create_archive(path_1_listing)
    except:
        print("Unable to upload files")
