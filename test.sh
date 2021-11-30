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
cd data
pwd
printf 'val1' > "2_${PREFIX}${OUTPUT}${SUFFIX}.${EXT}"
printf 'val2' > "1_${PREFIX}${OUTPUT}${SUFFIX}.${EXT}"
zip -r "${PREFIX}${OUTPUT}${SUFFIX}.zip" . -x ".*" -x "__MACOSX"
rm *.$EXT
cd ../.. 
clear; python3 main.py