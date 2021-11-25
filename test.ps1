$PYCMD = @"
import subprocess
from datetime import datetime;
now = datetime.now();
now_formated = now.strftime('%Y.%d.%m-%H.%M.%S.%f');
print(now_formated)
"@
$ROOT_DIR = "test"
$PREFIX = "pre_"
$SUFFIX = "_suf"
$OUTPUT = python -c $PYCMD
$EXT = "txt"
$DIRECTORIES = @("log", "data", "archive", "temp")
if (!(Test-Path -Path $ROOT_DIR ))
{
    New-Item -ItemType Directory -Path $ROOT_DIR
}
Set-Location -Path $ROOT_DIR
foreach ($DIR in $DIRECTORIES)
{
    if (!(Test-Path -Path $DIR ))
    {
        New-Item -ItemType "Directory" -Path $DIR
    }
}
$DUMMY_FILE_NAME = "$($PREFIX)$($OUTPUT)$($SUFFIX)"
Add-Content -Value "Dummy data" -Path "data\$DUMMY_FILE_NAME.$($EXT)"
$Compress = @{
    Path             = "data\$DUMMY_FILE_NAME.$($EXT)"
    CompressionLevel = "Fastest"
    DestinationPath  = "data\$DUMMY_FILE_NAME.zip"
}
Compress-Archive @Compress
Set-Location -Path ..
Clear-Host; python main.py
