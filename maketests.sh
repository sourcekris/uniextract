#!/bin/bash

POSITIONAL_ARGS=()
SKIP_DOSBOX=false
SKIP_WINE=false
DEBUG=false
SPECIFIC_TEST=""

# create maps for storing our tests in.
declare -A at_e at_c at_r   # archiver_test
declare -A wt_e wt_c wt_r   # wine_test
declare -A dt_e dt_c dt_r   # dosbox_test
declare -A bt_e bt_b        # blob_test

while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--test)
      SPECIFIC_TEST="$2"
      shift # past argument
      shift # past value
      ;;
    -d|--skip-dosbox)
      SKIP_DOSBOX=true
      shift # past argument
      ;;
    -w|--skip-wine)
      SKIP_WINE=true
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

# archiver_test stores a test for an archiver in the at_* hashmaps. Takes 4 arguments:
# - $1 - string - extension
# - $2 - string - user facing message for the test and what is written to the test archive.
# - $3 - string - archiver packing command
# - $4 - bool - does the test need to rm the original file (true / false)
function archiver_test () {
  at_e[$2]="$1"
  at_c[$2]="$3"
  at_r[$2]=$4
}

# does the archiver test we stored earlier in the global maps.
function archiver_test_do () {
  msg="$1"
  e="${at_e[$msg]}"
  cmdline="${at_c[$msg]}"
  rmorig=${at_r[$msg]}
  
  echo -n "$msg test: "
  echo -n "$msg" > 0
  eval "$cmdline"
  B64=$(gzip < 0.$e | base64 -w 0)

  rm 0.$e
  if [ $rmorig = true ]; then
    rm 0
  fi

  echo "$B64"
}

# blob_test stores test parameters an archive base64 blob:
# - $1 - string - extension
# - $2 - string - user facing message for the test
# - $3 - string - the base64 encoded archive
function blob_test () {
  bt_e[$2]="$1"
  bt_b[$2]="$3"
}

function blob_test_do () {
  msg="$1"
  e="${bt_e[$msg]}"
  blob="${bt_b[$msg]}"

  echo -n "$msg test: "
  B64=$(echo "$blob" | base64 -d > 0.$e && gzip < 0.$e | base64 -w 0)
  rm 0.$e

  echo "$B64"
}

# wine_test stores a test for an archiver that uses wine in the wt_* hashmaps. Takes 4 arguments:
# - $1 - string - extension
# - $2 - string - user facing message for the test and what is written to the test archive.
# - $3 - string - archiver packing command
# - $4 - bool - does the test need to rm the original file (true / false)
function wine_test () {
  wt_e[$2]="$1"
  wt_c[$2]="$3"
  wt_r[$2]=$4
}

# does the wine based test we stored earlier in the global maps.
function wine_test_do () {
  msg="$1"
  e="${wt_e[$msg]}"
  cmdline="${wt_c[$msg]}"
  rmorig=${wt_r[$msg]}
  
  echo -n "$msg test: "
  echo -n "$msg" > 0
  eval "$cmdline"
  B64=$(gzip < 0.$e | base64 -w 0)

  rm 0.$e
  if [ $rmorig = true ]; then
    rm 0
  fi

  echo "$B64"
}

function dosbox_test () {
  dt_e[$2]="$1"
  dt_c[$2]="$3"
  dt_r[$2]=$4
}

function dosbox_test_do () {
  e="${dt_e[$1]}"
  cmdline="${dt_c[$1]}"
  rmorig=${dt_r[$1]}

  eu=${e^^}
  
  echo -n "$1 test: "
  echo -n "$1" > 0
  #echo "cmdline: $cmdline"
  eval "$cmdline" > /dev/null
  B64=$(gzip < 0.$eu | base64 -w 0)

  rm -f 0.$e 0.$eu
  if [ $rmorig = true ]; then
    rm 0
  fi

  echo "$B64"
}

# Store the archiver tests in the hashmaps.
archiver_test "zip" "ZIP" "zip -q 0.\$e 0" true
archiver_test "cpio" "CPIO" "echo 0 | cpio -o --quiet -F 0.\$e" true
archiver_test "afio" "AFIO" "echo 0 | afio -o 0.\$e" true
archiver_test "kgb" "KGB" "tools/KGB_arch -9 0.\$e 0 > /dev/null" true
archiver_test "lzo" "LZOP" "lzop -9 -o 0.\$e 0" true
archiver_test "tar" "TAR" "tar -cf 0.\$e 0" true
archiver_test "gz" "GZ" "gzip < 0 > 0.\$e" true
archiver_test "rar" "RAR" "rar a -inul 0.\$e 0" true
archiver_test "7z" "7ZIP" "7z a 0.\$e 0 >/dev/null" true
archiver_test "arj" "ARJ" "arj a 0.\$e 0 > /dev/null" true
archiver_test "a" "AR" "atool -a -q 0.\$e 0" true
archiver_test "arc" "ARC" "arc an 0.\$e 0" true
archiver_test "Z" "Z" "compress -f 0" false
archiver_test "xz" "XZ" "xz -z 0" false
archiver_test "lrz" "LRZIP" "lrzip -q 0" true
archiver_test "rz" "RZIP" "rzip 0" false
archiver_test "lzma" "LZMA" "lzma 0" false
archiver_test "lz" "LZIP" "lzip 0" false
archiver_test "bz2" "BZIP2" "atool -a 0.\$e 0" false
archiver_test "lzh" "LZH" "jlha -aq9 0.\$e 0 2>/dev/null" true
archiver_test "uue" "UUE" "uuencode 0 0 > 0.\$e" true
archiver_test "xxe" "XXENC" "sfk xxenc 0 -tofile 0.\$e -yes -quiet" true
archiver_test "b64" "BASE64" "base64 0 > 0.\$e" true
archiver_test "adf" "ADF" "xdftool 0.\$e create + format 0 + write 0" true
archiver_test "hdf" "HDF" "xdftool 0.\$e create size=1M + format 0 + write 0" true
archiver_test "yenc" "YENC" "python -c \"__import__('yenc').encode('0','0.yenc')\"" true
archiver_test "cab" "CAB" "gcab -c 0.\$e 0" true
archiver_test "msi" "MSI" "msibuild 0.\$e -a 0 0" true
archiver_test "ihex" "IHEX" "objcopy -I binary 0 -O ihex 0.\$e" true
archiver_test "xxd" "XXD" "xxd 0 0.\$e" true
archiver_test "hex" "HEX" "xxd -p 0 0.\$e" true
archiver_test "mw" "MWSQUEEZE" "cat 0 | tools/mwsqueeze > 0.\$e" true
archiver_test "sz" "SNAPPYSZ" "tools/snzip 0" false
archiver_test "snz" "SNAPPYSNZIP" "tools/snzip -t snzip 0" false
archiver_test "raw" "SNAPPYRAW" "tools/snzip -t raw 0" false
archiver_test "iwa" "SNAPPYIWA" "tools/snzip -t iwa 0" false
archiver_test "snappy" "SNAPPYJAVA" "tools/snzip -t snappy-java 0" false
archiver_test "snappy" "SNAPPYHADOOP" "tools/snzip -t hadoop-snappy 0" false
archiver_test "zst" "FACEBOOKZSTD" "tools/zstd -q 0" true
archiver_test "lz4" "ZSTANDARDLZ4" "tools/zstd -q --format=lz4 0" true
archiver_test "zpaq" "ZPAQ" "zpaq a 0.zpaq 0 > /dev/null 2>&1" true

wine_test "bix" "BIX" "wine tools/bix a 0.\$e 0 > /dev/null" true
wine_test "ufa" "UFA" "wine tools/ufa a 0.\$e 0 > /dev/null" true
wine_test "777" "777" "wine tools/777 a 0.\$e 0 > /dev/null" true

dosbox_test "ain" "AIN" "dosbox -c \"mount d $(pwd)\" -c \"mount e tools\" -c \"d:\" -c \"e:\\scancode WaitForText 25,1 \\\"Press\\\",\\\"y\\\"\" -c \"e:\\ain a 0.\$e 0\" -c \"exit\"" true
dosbox_test "sqz" "SQUEEZIT" "dosbox -c \"mount d $(pwd)\" -c \"mount e tools\" -c \"d:\" -c \"e:\\sqz a 0 0\" -c \"exit\"" true
dosbox_test "lzw" "LZWCOM" "dosbox -c \"mount d $(pwd)\" -c \"mount e tools\" -c \"d:\" -c \"e:\\lzwcom 0 0.\$e\" -c \"exit\"" true
dosbox_test "amg" "AMG" "dosbox -c \"mount d $(pwd)\" -c \"mount e tools\" -c \"d:\" -c \"e:\\amgc a 0.\$e 0\" -c \"exit\"" true

blob_test "ace" "ACE" "TikxAAAAECoqQUNFKioUFAIA9CWcU3NysUtTIAAAFipVTlJFR0lTVEVSRUQgVkVSU0lPTir1+iAAAQEAAwAAAAMAAADGI5xTIAAAAMNoBKwAAwoAVEUBADBBQ0U="
blob_test "alz" "ALZIP" "QUxaAQoAAABCTFoBAQAghR6dUyAAAgC/b4hZBwAFADBz9InyDAAAQ0xaAQAAAAAAAAAAQ0xaAg=="
blob_test "egg" "EGG" "RUdHQQABpuPSNQAAAAAiguII45CFCgAAAAADAAAAAAAAAKyRhQoAAQAwC5WGLAAJAADg7qdn/NcBACKC4ggTDLUCAQUDAAAABQAAAMibkN4iguIIc3V3BwAiguII"
blob_test "sitx" "SITX" "U3R1ZmZJdCGhCpvdQhUzmVelAuMQEJyw11hPVhTvf7Gv8RF8KW4xgrunZoX/wAACArEbsZpRBUsFScxoSwpRFHcAAAADAAAAAVQA2Ke9dkwA/wIV3AYoWgJjWwEZJPL0HhcCFTtTweEC1woZmPZCiFECAlU="
blob_test "bin" "MacBinary" "AAEwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAN3yD6/d8hQ6AAAAbUJJTgAAAAAAAAAAAAAAAAAAAACBgeItAABNQUNCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
blob_test "as" "AppleSingle" "AAUWAAACAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAADAAAAPgAAAAEAAAAIAAAAPwAAABAAAAABAAAATwAAAAswKV8brylfIJ2AAAAAgAAAAEFQUExFU0lOR0xF"
blob_test "lzx" "LZX" "TFpYAAwACgQAAA8AAwAAAAMAAAAKAAAAAAoAAPXazQWuwSWjJjEkcAEwTFpY"
blob_test "zoo" "ZOO" "Wk9PIDIuMTAgQXJjaGl2ZS4aAADcp8T9KgAAANb///8CAAEAAAAAAAAD3KfE/QIAdAAAAHEAAACeUylzVdcDAAAAAwAAAAEAAAAAAAAAAAAwAAAAAAAAAAAAAAAACgB/EfwAAAAAAAAAAAAAQCkjKABaT0/cp8T9AgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD8gw=="
blob_test "cpz" "CPShrink" "AQAAAOsx0501D5i8MACwAPKuFOJMrwCbwfpdAgMAAAADAAAAnlOug0NQWg=="
blob_test "cru" "Crush" "Q1JVU0ggdjEuOAoaAHSgVwAAAgAAACAAAABDUlVDUlUAIFuMnlMDAAAAMC5UWFQAq9AjIn8AAAAAIK6OnlMDAAAAMS5UWFQAAAAAAAAAAAA="
blob_test "dgc" "DGC" "REdDQSAAAADAAQAAAAAAAAEAAAAQAAAADxvuajSXcFREQVRBIAAAADAAAAAAAAAAAAAAABAAAAADj3fKSBpLbkRHQ0MgAAAADAAAAAAAAAAAAAAAEAAAAHrxs0TmH4v6AAAAAAQAAABER0NBAAAAAElORk8gAAAAUAEAAAAAAAABAAAAEAAAANbVzwHT+wIpSUFSQyAAAABQAAAAAAAAAAAAAAAQAAAAs7RGNnCDOKQAAAAAIDAwMQAAAAAAAAAAsCChToH91wEAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAEAAAAAAAAAEAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAElGRFQgAAAAcAAAAAAAAAAAAAAAEAAAABp+VyKpydx/REdDQyAAAABIAAAAAAAAAAAAAAAQAAAA4AZ5kklgDhwAAAAAQAAAAPPmaJogAAAAM4gq/7X81wFhNMZCgf3XAQQAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAElGTk0gAAAAMAAAAAAAAAAAAAAAEAAAAFzm2x8rIbJRREdDQyAAAAANAAAAAAAAAAAAAAAQAAAA0RpaXp+2NZYAAAAABQAAAAEAAAAwAAAA"
blob_test "lbr" "LBR" "ACAgICAgICAgICAgAAABAN0CAAAAAAAAAAAAAAAAAAAAMCAgICAgICAgICABAAEA/moAAAAAAAAAAAAAAAAAAP8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMQlI="
blob_test "pma" "PMArc" "GKEtcG0yLREAAACAAAAAAAAAACAAAjAuXMvsoBIAAAAAALgAIHBpDWvkAAA="
blob_test "yyy" "crlzh" "dv0wLiAgIAAgIAAF5vc63k6Wk5oBfAF/digBDg=="
blob_test "qqq" "Squeeze" "dv9sDjAACAACAAEAuv8DAAcABQAEAAYArv+l/6r/hv+s/2//5f///jeqDW8C"
blob_test "sq2" "Squeeze2" "+v8wADAxLzAxLzEyMgAAGtYAIVRulwMAAQACAK7/rP/N///+0ho="
blob_test "zzz" "crunch" "dv4wLiAgIAAgIAABIZSKpOIZIACQPUAAwwE="
blob_test "sqx" "SQX" "ULBSAAAZAC1zcXgtCwAAAAAAAAAAAAAAAEeoRAAFLAAAAAAUFAJZ7cTYIAAAAKIJIlQcAAAACQAAAAkAdG1wXG1vb1wwZgQJAAAAAEAFAAAA4hxgOvvo3wimlDZDAAAnSz4rUwAABwA="
blob_test "acb" "ACB" "CoAIAIw5c+WZ55vfDOMOU+sK"

# Actually do the tests now.

# If the user requests a specific test, do it and exit now.
if [ ! -z "$SPECIFIC_TEST" ]; then
  if [ ${at_e[$SPECIFIC_TEST]+abc} ]; then
    archiver_test_do "$SPECIFIC_TEST"
  elif [ ${bt_e[$SPECIFIC_TEST]+abc} ]; then
    blob_test_do "$SPECIFIC_TEST"
  elif [ ${wt_e[$SPECIFIC_TEST]+abc} ]; then
    wine_test_do "$SPECIFIC_TEST"
  elif [ ${dt_e[$SPECIFIC_TEST]+abc} ]; then
    dosbox_test_do "$SPECIFIC_TEST"
  else
    echo "error: test $SPECIFIC_TEST not found."
  fi
  exit
fi

# Run all archiver tests.
for key in ${!at_e[@]}; do
  archiver_test_do "$key"
done

# Run all blob tests.
for key in ${!bt_e[@]}; do
  blob_test_do "$key"
done

if [ "$SKIP_DOSBOX" = false ]; then
    for key in ${!dt_e[@]}; do
      dosbox_test_do "$key"
    done
fi

if [ "$SKIP_WINE" = false ]; then
  for key in ${!wt_e[@]}; do
    wine_test_do "$key"
  done
fi

# Extra / Odd tests below...
echo -n "dar test: "
e=dar && td=$(mktemp -d) && echo -n DAR > $td/0 && pushd $td > /dev/null && dar -c 0 -q -X 0.1.$e && gzip < 0.1.$e | base64 -w 0 && popd > /dev/null && rm -fr $td && echo
