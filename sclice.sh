#!/bin/bash
# takes one and only argurments: the CALL_ID (CALL_ID.wav)
set -x
if [ -z "$1" ]
  then
    echo "call_id must be supplied"
    exit 1
  else
    CALL_ID=$1
fi
if [ -z "$2" ]
  then
    echo "fromLang be supplied"
    exit 1
  else
    FROM_LANG=$2
fi
if [ -z "$3" ]
  then
    echo "TO_LANG be supplied"
    exit 1
  else
    TO_LANG=$3
fi

if [ -z "$4" ]
  then
    echo "state be supplied, can either be 1(SIP) or 2(WEBSOCKET)"
    exit 1
  else
    SERVER_STATE=$4
fi

WAV_FILE=$CALL_ID.wav
LOG_FILE="$CALL_ID"_sclice.log
RESULT_FILE="$CALL_ID"_result.log
RATE=16000
> $LOG_FILE
> $RESULT_FILE
rm -rf $CALL_ID"_"*wav $CALL_ID"_"*mp3
if [ ! -f $WAV_FILE ]
  then
    echo "`pwd`/$WAV_FILE not found "
    exit 1
fi

if [ '1' = $SERVER_STATE ]
then
    RATE=16000
    MAX_TIME=50
    else
    RATE=8000
    MAX_TIME=3
fi

python bin_tail.py $WAV_FILE | auditok -r $RATE -m $MAX_TIME -s 0.3 -e 50 -n 0.5 -i - -o "$CALL_ID""_{N}_{start}-{end}.wav"  --debug-file $LOG_FILE &

tail -f $LOG_FILE | unbuffer -p grep -o $CALL_ID.*.wav | unbuffer -p grep -v tran | xargs -I {} python3 wavToText.py {} $FROM_LANG $TO_LANG $RATE
