#!/bin/bash

echo -n "ZIP test: "
e=zip && echo -n ZIP > 0 && zip -q 0.$e 0 && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "CPIO test: "
e=cpio && echo -n CPIO > 0 && echo 0 | cpio -o --quiet -F 0.$e && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "KGB test: "
e=kgb && echo -n KGB > 0 && tools/KGB_arch -9 0.$e 0 > /dev/null && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "LZOP test: "
e=lzo && echo -n LZOP > 0 && lzop -9 -o 0.$e 0 && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "TAR test: "
e=tar && echo -n TAR > 0 && tar -cf 0.$e 0 && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "GZIP test: "
e=gz && echo -n GZ > 0 && gzip < 0 > 0.$e && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "RAR test: "
e=rar && echo -n RAR > 0 && rar a -inul 0.$e 0 && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "7zip test: "
e=7z && echo -n 7ZIP > 0 && 7z a 0.$e 0 >/dev/null && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "ACE test: "
# we cannot create ACE archives on linux so heres one we created elsewhere.
e=ace && echo "TikxAAAAECoqQUNFKioUFAIA9CWcU3NysUtTIAAAFipVTlJFR0lTVEVSRUQgVkVSU0lPTir1+iAAAQEAAwAAAAMAAADGI5xTIAAAAMNoBKwAAwoAVEUBADBBQ0U=" | base64 -d > 0.$e && gzip < 0.$e | base64 -w 0 && rm 0.$e

echo -n "ARJ test: "
e=arj && echo -n ARJ > 0 && arj a 0.$e 0 > /dev/null && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "AR test: "
e=a && echo -n AR > 0 && atool -a -q 0.$e 0 && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "ARC test: "
e=arc && echo -n ARC > 0 && arc an 0.$e 0 && gzip < 0.$e | base64 -w 0 && rm 0 0.$e

echo -n "compress test: "
e=Z && echo -n Z > 0 && compress -f 0 && gzip < 0.$e | base64 -w 0 && rm 0.$e