#!/bin/bash

## rasp
export RESULT_DIR=/home/pi/reginaldojunior/experimentos/dynamic-batch/results
export REMOTE_DIR=/home/gcassales/bases
export LOCAL_DIR=/home/pi/reginaldojunior/comparison-xue3m-minibatching/datasets
export EXPER_ORDER_FILE=$RESULT_DIR/exper_order.log
export MOA_HOME=/home/pi/reginaldojunior/moa/moa-dynamic-batch

function Y {
  #Usage: $0 FILE ALGORITHM RATE
  Memory=900M
  echo "file: $1 algorithm: $2"

  declare -a esize=(25)
  mkdir -p $RESULT_DIR
  faux=${1##*\/}
  onlyname=${faux%%.*}
  nCores=8
  date +"%d/%m/%y %T"
  date +"%d/%m/%y %T" >> $EXPER_ORDER_FILE
  echo "ssh-${onlyname}-${2##*.}" >> ${RESULT_DIR}/ssh-log

  ssh gcassales@192.168.0.11 python socket-python-fuzzy.py 192.168.0.11 9004 ${REMOTE_DIR}/$1 >> ${RESULT_DIR}/ssh-log &
  sleep 30
  
  # echo "/usr/bin/java -Xshare:off -XX:+UseParallelGC -Xmx900M -cp $MOA_HOME/lib/:$MOA_HOME/lib/moa.jar moa.DoTask \"ChannelChunksTIMEDOptimized -l ($2 -s ${esize} -c ${nCores}) -s (ArffFileStream -f $1) -c 50 -e (BasicClassificationPerformanceEvaluator -o -p -r -f) -i -1 -d $RESULT_DIR/dump-${onlyname}-${2##*.}-${esize}-${nCores}\" > ${RESULT_DIR}/term-${onlyname}-${2##*.}-${esize}-${nCores}"
  IDENT="timedchunk"
  echo "$RESULT_DIR/${onlyname}-${2##*.}" >> ${EXPER_ORDER_FILE}
  /usr/bin/java -Xshare:off -XX:+UseParallelGC -Xmx900M -cp $MOA_HOME/lib/:$MOA_HOME/lib/moa.jar moa.DoTask "ChannelChunksTIMEDOptimized -l ($2 -s ${esize} -c ${nCores}) -s (ArffFileStream -f ${LOCAL_DIR}/$1) -c 50 -e (BasicClassificationPerformanceEvaluator -o -p -r -f) -i -1 -d $RESULT_DIR/dump-${onlyname}-${2##*.}-${esize}-${nCores}" > ${RESULT_DIR}/term-${onlyname}-${2##*.}-${esize}-${nCores}
  pidId=$(ssh gcassales@192.168.11 lsof -i:9004 | grep 9004 | awk '{print $2}')
  ssh gcassales@192.168.0.11 kill -9 $pidId
  sleep 30
  echo ""
  date +"%d/%m/%y %T"
  date +"%d/%m/%y %T" >> $EXPER_ORDER_FILE
}

function X {
  #Usage: $0 FILE ID RS RP RC
  # 1 -> sequential, 2 -> mb sem loop fusion, 3 -> mb com loop fusion
  declare -a algs=(
    "meta.AdaptiveRandomForestSequential" "meta.AdaptiveRandomForestExecutorMAXChunk"
    "meta.OzaBag" "meta.OzaBagExecutorMAXChunk"
    "meta.OzaBagAdwin" "meta.OzaBagAdwinExecutorMAXChunk"
    "meta.LeveragingBag" "meta.LBagExecutorMAXChunk"
    "meta.OzaBagASHT" "meta.OzaBagASHTExecutorMAXChunk"
    "meta.StreamingRandomPatches" "meta.StreamingRandomPatchesExecutorMAXChunk"
  )
  if [[ $2 == *"ARF"* ]]; then
    ID=0
  elif [[ $2 == "OBag" ]]; then
    ID=2
  elif [[ $2 == "OBagAd" ]]; then
    ID=4
  elif [[ $2 == "LBag" ]]; then
    ID=6
  elif [[ $2 == "OBagASHT" ]]; then
    ID=8
  elif [[ $2 == "SRP" ]]; then
    ID=10
  fi
  # Y $1 ${algs[${ID}]} "1" $4 "1"
  # Y $1 ${algs[$(( ID+1 ))]} $3 $5 "2"
  Y $1 ${algs[$(( ID+1 ))]} $3 $6 "3"
}

# alterar para o caminho do HD/scratch
mkdir -p $RESULT_DIR

# x dataset alg batch_size (seq) (mb-without-lf) (mb-lf)
X covtypeNorm.arff ARF
X covtypeNorm.arff LBag
X covtypeNorm.arff SRP
X covtypeNorm.arff OBagAd
X covtypeNorm.arff OBagASHT
X covtypeNorm.arff OBag

X airlines.arff ARF
X airlines.arff LBag
X airlines.arff SRP
X airlines.arff OBagAd
X airlines.arff OBagASHT
X airlines.arff OBag

X elecNormNew.arff ARF
X elecNormNew.arff LBag
X elecNormNew.arff SRP
X elecNormNew.arff OBagAd
X elecNormNew.arff OBagASHT
X elecNormNew.arff OBag

X GMSC.arff ARF
X GMSC.arff LBag
X GMSC.arff SRP
X GMSC.arff OBagAd
X GMSC.arff OBagASHT
X GMSC.arff OBag

date +"%d/%m/%y %T" >> $EXPER_ORDER_FILE