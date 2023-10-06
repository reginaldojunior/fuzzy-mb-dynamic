
## rasp
export MOA_HOME=/home/pi/reginaldojunior/moa/moa-release-2019.05.1-SNAPSHOT/
export RESULT_DIR=/home/pi/reginaldojunior/experimentos/mb-and-mblf/
export REMOTE_DIR=/home/gcassales/bases/
export LOCAL_DIR=/home/pi/reginaldojunior/comparison-xue3m-minibatching/datasets
export EXPER_ORDER_FILE=$RESULT_DIR/exper_order.log

function Y {
  #Usage: $0 FILE ALGORITHM RATE
  Memory=700M
  echo "file: $1 algorithm: $2 batch_size: $3"

  declare -a esize=(25)
  mkdir -p $RESULT_DIR
  faux=${1##*\/}
  onlyname=${faux%%.*}
  bsize=${3}
  rate=${4}
  nCores=4
  date +"%d/%m/%y %T"
  date +"%d/%m/%y %T" >> $EXPER_ORDER_FILE
  echo "ssh-${onlyname}-${2##*.}-${bsize}" >> ${RESULT_DIR}/ssh-log
  ssh gcassales@192.168.0.11 java SocketJavaDynamic 192.168.0.11 9004 ${REMOTE_DIR}/$1 >> ${RESULT_DIR}/ssh-log &
  
  sleep 3
  if [[ $2 == *"MAX"* ]]; then
    #CHUNK
    IDENT="timedchunk"
    echo "$RESULT_DIR/${onlyname}-${2##*.}-${esize}-${nCores}-${bsize}" >> ${EXPER_ORDER_FILE}
    java -Xshare:off -XX:+UseParallelGC -Xmx$Memory -cp $MOA_HOME/lib/:$MOA_HOME/lib/moa.jar moa.DoTask "ChannelChunksTIMEDOptimized -l ($2 -s ${esize} -c ${nCores}) -s (ArffFileStream -f ${LOCAL_DIR}/$1) -t 120 -c ${bsize} -e (BasicClassificationPerformanceEvaluator -o -p -r -f) -i -1 -d $RESULT_DIR/dump-${onlyname}-${2##*.}-${esize}-${nCores}-${bsize}" > ${RESULT_DIR}/term-${onlyname}-${2##*.}-${esize}-${nCores}-${bsize}
  elif [[ ${2} == *"RUNPER"* ]]; then
    #PARALLEL
    IDENT="timedinterleaved"
    echo "$RESULT_DIR/${onlyname}-${2##*.}-${esize}-${nCores}-1" >> ${EXPER_ORDER_FILE}
    java -Xshare:off -XX:+UseParallelGC -Xmx$Memory -cp $MOA_HOME/lib/:$MOA_HOME/lib/moa.jar moa.DoTask "ChannelTIMED -l ($2 -s ${esize} -c ${nCores}) -s (ArffFileStream -f ${LOCAL_DIR}/$1) -t 120 -e (BasicClassificationPerformanceEvaluator -o -p -r -f) -i -1 -d $RESULT_DIR/dump-${onlyname}-${2##*.}-${esize}-${nCores}-1" > ${RESULT_DIR}/term-${onlyname}-${2##*.}-${esize}-${nCores}-1
  else
    #SEQUENTIAL OR PARALLEL
    IDENT="timedinterleaved"
    echo "$RESULT_DIR/${onlyname}-${2##*.}-${esize}-1-1" >> ${EXPER_ORDER_FILE}
    java -Xshare:off -XX:+UseParallelGC -Xmx$Memory -cp $MOA_HOME/lib/:$MOA_HOME/lib/moa.jar moa.DoTask "ChannelTIMED -l ($2 -s ${esize}) -s (ArffFileStream -f ${LOCAL_DIR}/$1) -t 120 -e (BasicClassificationPerformanceEvaluator -o -p -r -f) -i -1 -d $RESULT_DIR/dump-${onlyname}-${2##*.}-${esize}-1-1" > ${RESULT_DIR}/term-${onlyname}-${2##*.}-${esize}-1-1
  fi
  echo ""
  date +"%d/%m/%y %T"
  date +"%d/%m/%y %T" >> $EXPER_ORDER_FILE
}


function X {
  #Usage: $0 FILE ID RS RP RC
  declare -a algs=(
  "meta.AdaptiveRandomForestSequential" "meta.AdaptiveRandomForestExecutorRUNPER" "meta.AdaptiveRandomForestExecutorMAXChunk"
  "meta.OzaBag" "meta.OzaBagExecutorRUNPER" "meta.OzaBagExecutorMAXChunk"
  "meta.OzaBagAdwin" "meta.OzaBagAdwinExecutorRUNPER" "meta.OzaBagAdwinExecutorMAXChunk"
  "meta.LeveragingBag" "meta.LBagExecutorRUNPER" "meta.LBagExecutorMAXChunk"
  "meta.OzaBagASHT" "meta.OzaBagASHTExecutorRUNPER" "meta.OzaBagASHTExecutorMAXChunk"
  "meta.StreamingRandomPatches" "meta.StreamingRandomPatchesExecutorRUNPER" "meta.StreamingRandomPatchesExecutorMAXChunk"
  )
  if [[ $2 == *"ARF"* ]]; then
    ID=0
  elif [[ $2 == "OBag" ]]; then
    ID=3
  elif [[ $2 == "OBagAd" ]]; then
    ID=6
  elif [[ $2 == "LBag" ]]; then
    ID=9
  elif [[ $2 == "OBagASHT" ]]; then
    ID=12
  elif [[ $2 == "SRP" ]]; then
    ID=15
  fi
  # Y /home/pi/reginaldojunior/comparison-xue3m-minibatching/datasets/ ${algs[${ID}]} $3 $4
  # Y /home/pi/reginaldojunior/comparison-xue3m-minibatching/datasets/ ${algs[$(( ID+1 ))]} $3 $5
  Y $1 ${algs[$(( ID+2 ))]} $3
}

# alterar para o caminho do HD/scratch
mkdir -p $RESULT_DIR

X covtypeNorm.arff ARF 50
X covtypeNorm.arff LBag 50 
X covtypeNorm.arff SRP 50
X covtypeNorm.arff OBagAd 50
X covtypeNorm.arff OBagASHT 50
X covtypeNorm.arff OBag 50

X airlines.arff ARF 50
X airlines.arff LBag 50
X airlines.arff SRP 50
X airlines.arff OBagAd 50
X airlines.arff OBagASHT 50
X airlines.arff OBag 50

X elecNormNew.arff ARF 50
X elecNormNew.arff LBag 50
X elecNormNew.arff SRP 50
X elecNormNew.arff OBagAd 50
X elecNormNew.arff OBagASHT 50
X elecNormNew.arff OBag 50

X GMSC.arff ARF 50
X GMSC.arff LBag 50
X GMSC.arff SRP 50
X GMSC.arff OBagAd 50
X GMSC.arff OBagASHT 50
X GMSC.arff OBag 50 

date +"%d/%m/%y %T" >> $EXPER_ORDER_FILE