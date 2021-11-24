PYCMD=$(cat <<EOF
import subprocess
from datetime import datetime;
now = datetime.now();
now_formated = now.strftime("%Y.%d.%m-%H.%M.%S.%f");
print(now_formated)
EOF
    )
ROOT_DIR="test"
PREFIX="pre_"
SUFFIX="_suf"
OUTPUT=$(python3 -c "$PYCMD")
EXT="txt"
mkdir "${ROOT_DIR}"
cd "${ROOT_DIR}"
mkdir log data archive temp
printf '' > "data/${PREFIX}${OUTPUT}${SUFFIX}.${EXT}"
zip "data/${PREFIX}${OUTPUT}${SUFFIX}.zip" "data/${PREFIX}${OUTPUT}${SUFFIX}.${EXT}"
cd ..
clear; python3 main.py