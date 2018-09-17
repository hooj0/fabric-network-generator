#!/bin/bash

COMPOSE_FILE=docker-compose-cli.yaml
COMPOSE_FILE_COUCH=docker-compose-couch.yaml
COMPOSE_FILE_MONITORING=docker-compose-prom.yaml
COMPOSE_FILE_VISUALIZER=docker-compose-visualizer.yaml
COMPOSE_FILE_EXTERNAL_NET=docker-compose-fabric-monitor.yaml
COMPOSE_FILE_COMMONS="docker-compose-fabric.yaml -f docker-compose-zookeeper-kafka.yaml"

function printHelp () {
cat << HELP
USAGE: $0 [OPTIONS] COMMANDS

OPTIONS: 
  -h     use the help manual.
  -f     COMPOSE_FILE, setting docker-compose file.
  -n     CHANNEL_NAME, docker-compose cli required channel name(default: mychannel).
  -t     CLI_TIMEOUT, docker-compose cli required request timeout(default: 10000)
  -c     cli mode: run docker-compose command start, use docker-compose-cli.yaml
  -e     e2e mode: run docker-compose command start, use docker-compose-fabric-*.yaml
  -d     add couchdb service, use docker-compose-couchdb.yaml
  -v     add visualizer service, use docker-compose-visualizer.yaml
  -m     add prom monitor service, use ${COMPOSE_FILE_MONITORING}


COMMANDS:
  up          start docker container & create container/network/images
  down        stop(kill) docker container & clean container/network/images resources
  restart     run the down command and then run the up command.
  clean       clean docker network & container & images resources
  deploy      deploy fabric service stack swarm
  remove      remove fabric service stack swarm
  help        use the help manual.
    
EXAMPLES: 
  $0 -h
  $0 help

  $0 up
  $0 restart
  $0 down
  $0 clean
  
  $0 -c -n mychannel -t 2000 up
  $0 -f docker-compose-prom.yaml up
  $0 -e up
  $0 -e -d -v -m up
  $0 -edvm up
  $0 -edvm clean up

  $0 -edvm deploy
  $0 -edvm remove
  
HELP
exit 0
}

function validateArgs () {
    #log yellow "############################ validate args ########################### "
    
    if [ $# -lt 1 ]; then
        #log red "Empty args options, Option up / down / restart not mentioned"
        printHelp
        exit 1
    fi     
}

function defaultSettings() {
    if [ -z "${CHANNEL_NAME}" ]; then
        log yellow "setting to default channel 'mychannel'"
        CHANNEL_NAME=mychannel
    fi
    
    if [ "$IF_CA_MODE" == "ca" ]; then
        COMPOSE_FILE=docker-compose-e2e-${FABRIC_NETWORK_CONFIGTX_VERSION}.yaml
        log yellow "setting to COMPOSE_FILE [${COMPOSE_FILE}]"
    fi
    echo
}

function clearContainers () {
    log yellow "########################## clean container ########################### "
    
    CONTAINER_IDS=$(docker ps -aq)
    if [ -z "$CONTAINER_IDS" -o "$CONTAINER_IDS" = " " ]; then
        log sky_blue "---- No containers available for deletion ----"
    else
        log purple "==> remove docker containers: ${CONTAINER_IDS}"
        docker rm -f $CONTAINER_IDS
    fi
    echo
}

function removeUnwantedImages() {
    log yellow "######################## clean unwanted images ####################### "

    DOCKER_IMAGE_IDS=$(docker images | grep "dev\|none\|test-vp\|peer[0-9]-" | awk '{print $3}')
    if [ -z "$DOCKER_IMAGE_IDS" -o "$DOCKER_IMAGE_IDS" = " " ]; then
        log sky_blue "---- No images available for deletion ----"
    else
        log purple "==> remove docker images: $DOCKER_IMAGE_IDS"
        docker rmi -f $DOCKER_IMAGE_IDS
    fi
    echo
}

function cleanDataStore(){
    log yellow "########################### clean data store ######################### "
    
    log purple "clean hyperledger store data"
    rm -rfv /var/hyperledger/* /etc/hyperledger/*

    mkdir -pv /var/fabric/config
    log purple "clean hyperledger fabric key value store"
    rm -fv /var/fabric/config/fabric-kv-store.properties
    echo
}

# disabled
function cleanNetwork() {
    log yellow "############################ clean network ########################### "
    
    lines=`docker ps -a | grep 'dev-peer' | wc -l`

    if [ "$lines" -gt 0 ]; then
        docker ps -a | grep 'dev-peer' | awk '{print $1}' | xargs docker rm -f
    fi

    lines=`docker images | grep 'dev-peer' | grep 'dev-peer' | wc -l`
    if [ "$lines" -gt 0 ]; then
        docker images | grep 'dev-peer' | awk '{print $1}' | xargs docker rmi -f
    fi

    lines=`docker ps -aq | wc -l`
    if ((lines > 0)); then
        docker stop $(docker ps -aq)
        docker rm $(docker ps -aq)
    fi

    lines=`docker network ls -f 'name=fabric_blockchain_net' | wc -l`
    if ((lines > 1)); then
        docker network rm fabric_blockchain_net
    fi
    
    echo
}

function checkNetworkConfigs() {
  if [ ! -d "./fabric-configs/${FABRIC_NETWORK_CONFIGTX_VERSION}/crypto-config" ]; then
      log red "fabric-configs/${FABRIC_NETWORK_CONFIGTX_VERSION}/crypto-config directory not exists."
      #source ./fabric-configs/generate.sh -v ${FABRIC_NETWORK_CONFIGTX_VERSION} -c ${CHANNEL_NAME} clean gen merge
      log _blue "\nPlease generate the required [crypto-config] files\nExample:"
      log _blue "\t cd fabric-configs \n\t sudo sh generate.sh -v ${FABRIC_NETWORK_CONFIGTX_VERSION} -c ${CHANNEL_NAME} clean gen merge"
      exit 1
    fi

    if [ ! -f "./fabric-configs/${FABRIC_NETWORK_CONFIGTX_VERSION}/channel-artifacts/${CHANNEL_NAME}.tx" ]; then
      log red "fabric-configs/${FABRIC_NETWORK_CONFIGTX_VERSION}/channel-artifacts/${CHANNEL_NAME}.tx file not exists."
      #source ./fabric-configs/generate.sh -v ${FABRIC_NETWORK_CONFIGTX_VERSION} -c ${CHANNEL_NAME} gen-channel 
      log _blue "\nPlease generate the required [${CHANNEL_NAME}.tx] files\nExample:"
      log _blue "\t cd fabric-configs \n\t sudo sh generate.sh -v ${FABRIC_NETWORK_CONFIGTX_VERSION} -c ${CHANNEL_NAME} gen-channel"
      exit 1
    fi
}


function networkUp () {
    log yellow "######################## start fabric network ######################## "
    
    checkNetworkConfigs

    if [ ! -z "${REPLENISH_COMPOSE_FILE}" ]; then
      log purple "==> docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE $REPLENISH_COMPOSE_FILE up -d "
      docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE $REPLENISH_COMPOSE_FILE up
    else
      log purple "==> docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE up -d "
      docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE up
    fi

    #if [ $? -ne 0 ]; then
        #log red "ERROR !!!! Unable to pull the images "
        #exit 1
    #fi

    #echo "==> docker logs -f cli"
    #echo
    #docker logs -f cli
    echo
}

function networkDown () {
    log yellow "#################### stop & remove fabric network #################### "
    
    if [ ! -z "${REPLENISH_COMPOSE_FILE}" ]; then
      log purple "==> docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE $REPLENISH_COMPOSE_FILE down"
      docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE $REPLENISH_COMPOSE_FILE down
    else
      log purple "==> docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE down"
      docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE down
    fi
    echo
    
    #Cleanup the chaincode containers
    clearContainers

    #Cleanup images
    removeUnwantedImages
    
    #Cleanup data store
    cleanDataStore    
    echo
} 

function deployStack() {
    log yellow "################ deploy services stack fabric network ################# "

    checkNetworkConfigs
    
    if [ "${ENABLED_MONITOR}" == "true" ]; then
        ADMIN_USER=admin \
        ADMIN_PASSWORD=admin \
        SLACK_URL=https://hooks.slack.com/services/TOKEN \
        SLACK_CHANNEL=devops-alerts \
        SLACK_USER=alertmanager \
        docker stack deploy -c ${COMPOSE_FILE_MONITORING} monitor
    fi

    if [ ! -z "${REPLENISH_COMPOSE_FILE}" ]; then
      log purple "==> docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE $REPLENISH_COMPOSE_FILE config > docker-compose.stack.yml"
      docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE $REPLENISH_COMPOSE_FILE config > docker-compose.stack.yml
      
      #COMPOSE_FILE_COMMONS=`echo $COMPOSE_FILE_COMMONS | sed 's/ -f/ -c/g'`
      #REPLENISH_COMPOSE_FILE=`echo $REPLENISH_COMPOSE_FILE | sed 's/ -f/ -c/g'`
      #log purple "==> docker stack deploy -c $COMPOSE_FILE_COMMONS -c $COMPOSE_FILE $REPLENISH_COMPOSE_FILE fabric"
      #docker stack deploy -c $COMPOSE_FILE_COMMONS -c $COMPOSE_FILE $REPLENISH_COMPOSE_FILE fabric
    else
      log purple "==> docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE config > docker-compose.stack.yml"
      docker-compose -f $COMPOSE_FILE_COMMONS -f $COMPOSE_FILE config > docker-compose.stack.yml

      #COMPOSE_FILE_COMMONS=`echo $COMPOSE_FILE_COMMONS | sed 's/ -f/ -c/g'`
      #log purple "==> docker stack deploy -c $COMPOSE_FILE_COMMONS -c $COMPOSE_FILE fabric"
      #docker stack deploy -c $COMPOSE_FILE_COMMONS -c $COMPOSE_FILE fabric
    fi


    if [ -f "docker-compose.stack.yml" ]; then
      log purple "==> docker stack deploy -c docker-compose.stack.yml fabric"
      docker stack deploy -c docker-compose.stack.yml fabric      
    else
      log red "==> docker-compose.stack.yml not found!!!"
      exit 1  
    fi

    if [ "${ENABLED_MONITOR}" == "true" ]; then
      log purple "==> monitor stack list"
      docker stack ps monitor
    fi    
    log purple "==> fabric stack fabric list"   
    docker stack ps fabric

    log purple "==> fabric service list" 
    docker service ls
}


function removeStack() {
    log yellow "################ remove services stack fabric network ################# "

    if [ "${ENABLED_MONITOR}" == "true" ]; then
        docker stack rm monitor fabric    
    fi    
    docker stack rm fabric

    if [ -f "docker-compose.stack.yml" ]; then
      log purple "==> rm -rfv docker-compose.stack.yml"
      rm -rfv docker-compose.stack.yml     
    fi
}


# import
#--------------------------------------------------------------------------
source ./scripts/log.sh
source .env


# check args
#--------------------------------------------------------------------------
validateArgs $@


# usage options
# -------------------------------------------------------------------------------
printf "\n\n"
echo "参数列表：$*"

while getopts ":f:n:t:cedmhvs" opt; do

    printf "选项：%s, 参数值：$OPTARG \n" $opt
    case $opt in
        c ) 
            COMPOSE_FILE=docker-compose-cli.yaml
        ;;
        e ) 
            COMPOSE_FILE=docker-compose-fabric-${FABRIC_NETWORK_CONFIGTX_VERSION}.yaml
        ;;
        f ) 
            COMPOSE_FILE=$OPTARG
        ;;
        n ) 
            CHANNEL_NAME=$OPTARG
        ;;
        t ) 
            CLI_TIMEOUT=$OPTARG
        ;;
        d ) 
            REPLENISH_COMPOSE_FILE="${REPLENISH_COMPOSE_FILE} -f ${COMPOSE_FILE_COUCH}"
        ;;
        v ) 
            REPLENISH_COMPOSE_FILE="${REPLENISH_COMPOSE_FILE} -f ${COMPOSE_FILE_VISUALIZER}"
        ;;
        m ) 
            REPLENISH_COMPOSE_FILE="${REPLENISH_COMPOSE_FILE} -f ${COMPOSE_FILE_EXTERNAL_NET}"
            ENABLED_MONITOR="true"
        ;;
        h ) 
            printHelp
        ;; 
        ? ) echo "error" exit 1;;
    esac
done

shift $(($OPTIND - 1))
echo "命令参数：$*"


# varibles
#--------------------------------------------------------------------------
REPLENISH_COMPOSE_FILE="$(echo $REPLENISH_COMPOSE_FILE)"

: ${ENABLED_MONITOR:="false"}
: ${CHANNEL_NAME:="mychannel"}
: ${CLI_TIMEOUT:="10000"}

log red "FABRIC_NETWORK_CONFIGTX_VERSION=${FABRIC_NETWORK_CONFIGTX_VERSION}"
log red "COMPOSE_FILE=${COMPOSE_FILE}"
log red "REPLENISH_COMPOSE_FILE=${REPLENISH_COMPOSE_FILE}"
log red "CHANNEL_NAME=${CHANNEL_NAME}"
log red "TIMEOUT=${CLI_TIMEOUT}"
echo

export CHANNEL_NAME=${CHANNEL_NAME}
export TIMEOUT=${CLI_TIMEOUT}


# Create the network using docker compose process
# ------------------------------------------------------------------------------
for opt in $*; do
    case "$opt" in
        up|start)
            networkUp
        ;;
        down|stop)
            networkDown
        ;;
        restart)
            networkDown
            networkUp
        ;;
        clean)
            networkDown
            cleanNetwork
        ;;
        deploy)
            deployStack
        ;;
        remove)
            removeStack
        ;;
        *)
            printHelp
            exit 1
        ;;
    esac
done
