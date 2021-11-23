# scp-s3-uploader

A Python script to upload every file from a given path to an AWS S3 bucket.
The Python script uses the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library.

---

## Install packages from requirements.txt file

```
pip install -r requirements.txt
```

---

## Running local test and debugging

- Create directories
  - log directory
  - temp directory
  - archive directory
  - data directory

```
# Create directoris example
mkdir _log test temp archive
```

- Update .yml file paths
  - log directory --> LOG_ROOT
  - temp directory --> TEMP_ROOT
  - archive directory --> ARCHIVE_ROOT
  - data directory --> LOKAL_ROT

```
# Updated .yml file paths example
LOG_ROOT: _log
LOCAL_ROOT: test
TEMP_ROOT: temp
ARCHIVE_ROOT: archive
```
