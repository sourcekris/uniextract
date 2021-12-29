#!/bin/bash

echo -n "ZIP test: "
echo -n ZIP > 0 && zip -q 0.zip 0 && gzip < 0.zip | base64 -w 0 && rm 0 0.zip

echo -n "CPIO test: "
echo -n CPIO > 0 && echo 0 | cpio -o --quiet -F 0.cpio && gzip < 0.cpio | base64 -w 0 && rm 0 0.cpio

echo -n "KGB test: "
echo -n KGB > 0 && tools/KGB_arch -9 0.kgb 0 > /dev/null && gzip < 0.kgb | base64 -w 0 && rm 0 0.kgb