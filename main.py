__author__ = "Owen Corcoran"
__copyright__ = "Copyright 2019"
__version__ = "0.0.1"
__maintainer__ = "Owen Corcoran"
__email__ = "cyperplex@gmail.com"
__information__ = "Simple script to backup files to S3 using IAM, S3 Bucket. This will require the presence of an IAM account, S3 bucket with associated access policy and role assigned to the iam user to write data"

import json, boto3, logging, time, os
from botocore.exceptions import ClientError

config_dictionary = {}

def read_json_config(filename):
    '''
    Function to read the json config file provided with aws creds and remote bucket name
    :param filename:  Config file name
    :return: config dictionary for parsing into credential key:value elements for boto3 request
    '''
    with open(filename) as json_data_file:
        config_dictionary = json.load(json_data_file)
        return config_dictionary

def upload_s3(config_dictionary, path, bucket_suffix):
    '''
    :param config_dictionary: directory where the configuration file is located for reading
    :param path: provided local path for backup
    :param bucket_suffix: suffix name  for the backup folder which is appended after date, to describe the files being backed up
    :return: return false or true depending on success
    '''
    print("Hello ", os.getlogin(), ", lets backup")
    try:
        print("Upload file to Amazon S3")
        for root,dirs,files in os.walk(path):
            total_file_number = len(files)
            file_count = total_file_number
            print("Opening following path", path)
            for file in files:
                print("Processing file", file)
                s3_client = boto3.resource(
                    's3',
                    aws_access_key_id=config_dictionary['s3']['access-key'],
                    aws_secret_access_key=config_dictionary['s3']['secret-access-key']
                )
                try:
                    tdate = time.strftime("%Y.%m.%d")
                    fullfoldername = tdate + "_" + bucket_suffix + "/"
                    s3_client.meta.client.upload_file(os.path.join(root,file), config_dictionary['s3']['bucket'], fullfoldername + file)
                    print(file_count, " of files processed out of ", total_file_number)
                    file_count = (file_count - 1)
                except Exception  as ex:
                    print("exception error" , ex)
                    file_count = (file_count - 1)
                    print("Unable to make S3 upload request for ", file, "Total files left: ",file_count, " out of: ", total_file_number)
    except ClientError as e:
        logging.error(e)
        return False
    return True

if __name__ == '__main__':
   # Try call the Main function to create objects
    configuration = read_json_config('config.json')
    #print("Loading Configuration", json.dumps(configuration, indent=4))
    upload_s3(configuration,r"C:\testFolder", "pictures")
