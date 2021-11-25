# scp-s3-uploader

## General description

The Python script uses the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library to upload every file from a given path to an AWS S3 bucket.\
Before uploading files to s3 the script moves files into a temporary folder to make sure the file is not being written to, which can be a problem in Windows.\
To be able to authenticate against AWS a secrets.yml file is required.\
Even though a good rule of thumb is to never store any sensitive information in paths.. Just to be sure.. file paths are also set in the secrets.yml file.\
Logging is configured in the config.yml as well as opt-in-out settings to suit different needs.\
<br/>

---

## Install packages from requirements.txt file

```
pip install -r requirements.txt
```

---

## Running local test and debugging

- Update secrets.yml file
  - log directory --> LOG_ROOT
  - temp directory --> TEMP_ROOT
  - archive directory --> ARCHIVE_ROOT
  - data directory --> DATA_ROOT

```
# secrets.yml file example
LOG_ROOT: test/_log
DATA_ROOT: test/data
TEMP_ROOT: test/temp
ARCHIVE_ROOT: test/archive
```

- Create directories
  - log directory
  - temp directory
  - archive directory
  - data directory

```
# Run test.sh test.sh to setup test environment and run a quick test with some dummy data.

chmod +x test.sh && ./test.sh;

```
