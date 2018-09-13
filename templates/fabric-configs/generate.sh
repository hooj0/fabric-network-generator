#!/bin/bash

#set -e
#set -uo pipefail
trap "echo 'error: Script failed: see failed command above'" ERR


# import files
# -------------------------------------------------------------------------------
. ../scripts/log.sh

# common variables
# -------------------------------------------------------------------------------
FABRIC_ROOT="/opt/gopath/src/github.com/hyperledger/fabric"
export FABRIC_ROOT=$FABRIC_ROOT
export FABRIC_CFG_PATH=$PWD

log purple "FABRIC_ROOT=${FABRIC_ROOT}"
log purple "FABRIC_CFG_PATH=${FABRIC_CFG_PATH}"
echo

OS_ARCH=$(echo "$(uname -s|tr '[:upper:]' '[:lower:]'|sed 's/mingw64_nt.*/windows/')-$(uname -m | sed 's/x86_64/amd64/g')" | awk '{print tolower($0)}')

function usageHelp() {
cat << HELP
USAGE: $0 [OPTIONS] COMMANDS

OPTIONS: 
  -h help           use the help manual.
  -v version        fabric configtx generate config version(default: v1.1).
  -c channel        generate channel configtx files(default: mycc)
  -a anchor peer    generate anchor peer config tx files

COMMANDS:
  clean           clean store & config
  gen             generate channel & artifacts & certificates
  gen-channel     generate "increment" channel configtx artifacts
  merge           merge channel & artifacts & certificates to version directory
  regen           regenerate channel & artifacts & certificates
    
EXAMPLES: 
  $0 -h
  $0 help

  $0 -v v1.1 -c mycc gen
  $0 -v v1.1 -c mycc gen merge
  $0 -v v1.1 -c mycc regen
  $0 -v v1.1 -c mycc regen merge
  $0 -c mychannel -c mycc gen-channel
  $0 -c mychannel -v v1.2 gen-channel
    
  $0 -a -c mychannel -c mycc clean gen-channel
  $0 -c mychannel -v v1.1 merge
  $0 -c mychannel -v v1.1 clean
    
HELP
exit 0
}

function validateArgs () {
    #log yellow "############################ validate args ########################### "
    
    if [ $# -lt 1 ]; then
        log red "$0 exec args eq 0: $#"
        usageHelp
        exit 1
    fi     
}

## Using docker-compose template replace private key file names with constants
function replacePrivateKey () {
    echo
    echo "##########################################################"
    echo "#####         replace certificates  key          #########"
    echo "##########################################################"
    
    ARCH=`uname -s | grep Darwin`
    echo "ARCH: $ARCH"
    if [ "$ARCH" == "Darwin" ]; then
        OPTS="-it"
    else
        OPTS="-i"
    fi
    echo "OPTS: $OPTS"

    echo
    log yellow "==> cp -rv ../docker-compose-fabric-template.yaml ../docker-compose-fabric-$VERSION_DIR.yaml"
    cp -rv ../docker-compose-fabric-template.yaml docker-compose-fabric-${VERSION_DIR}.yaml

    CURRENT_DIR=$PWD
    {% for peer in peers %}
    cd ./$CRYPTO_CONFIG_LOCATION/peerOrganizations/%{peer.name | lower }.%{peer.domain | lower }/ca/
    PRIV_KEY=$(ls *_sk)
    cd $CURRENT_DIR

    sed $OPTS "s/CA%{loop.index0}_PRIVATE_KEY/${PRIV_KEY}/g" "docker-compose-fabric-${VERSION_DIR}.yaml"

    {% endfor %}

#    cd ./$CRYPTO_CONFIG_LOCATION/peerOrganizations/org2.bar.com/ca/
#    PRIV_KEY=$(ls *_sk)
#    cd $CURRENT_DIR
#
#    sed $OPTS "s/CA2_PRIVATE_KEY/${PRIV_KEY}/g" "docker-compose-fabric-${VERSION_DIR}.yaml"
    
    mv -vf docker-compose-fabric-${VERSION_DIR}.yaml ../docker-compose-fabric-${VERSION_DIR}.yaml
    log done "replace sk"
    echo
}

## Generates Org certs using cryptogen tool
function generateCerts() {
    CRYPTOGEN=$FABRIC_ROOT/release/$OS_ARCH/bin/cryptogen

    if [ -f "$CRYPTOGEN" ]; then
        log yellow "Using cryptogen -> $CRYPTOGEN"
        log done "check crypto"
    else
        log yellow "Building cryptogen"
        log yellow "===> make -C $FABRIC_ROOT release"
        make -C $FABRIC_ROOT release
        log done "make crypto"
    fi

    echo
    echo "##########################################################"
    echo "##### Generate certificates using cryptogen tool #########"
    echo "##########################################################"

    log yellow "==> cryptogen generate --config=./$CRYPTO_CONFIG_FILE --output=./$CRYPTO_CONFIG_LOCATION"
    $CRYPTOGEN generate --config=./$CRYPTO_CONFIG_FILE --output=./$CRYPTO_CONFIG_LOCATION
    
    log done "generate crypto"
    echo
}

## Generate orderer genesis block , channel configuration transaction and anchor peer update transactions
function checkConfigtxgen() {
    CONFIGTXGEN=$FABRIC_ROOT/release/$OS_ARCH/bin/configtxgen
    
    if [ -f "$CONFIGTXGEN" ]; then
        log yellow "Using configtxgen -> $CONFIGTXGEN"
        
        log done "check Configtxgen"
    else
        log yellow "Building configtxgen"
        log yellow "===> make -C $FABRIC_ROOT release"
        make -C $FABRIC_ROOT release
        
        log done "make Configtxgen"
    fi
}

function generateGenesisBlock() {
    echo
    echo "##########################################################"
    echo "#########  Generating Orderer Genesis block ##############"
    echo "##########################################################"
    # Note: For some unknown reason (at least for now) the block file can't be
    # named orderer.genesis.block or the orderer will fail to launch!
    log yellow "==> cryptogen -profile TwoOrgsOrdererGenesis${version} -outputBlock ./$CHANNEL_ARTIFACTS_LOCATION/genesis.block"
    $CONFIGTXGEN -profile TwoOrgsOrdererGenesis${version} -outputBlock ./$CHANNEL_ARTIFACTS_LOCATION/genesis.block
    
    log done "generate genesis.block"
    echo
}

function generateChannelArtifacts() {
    echo
    echo "#################################################################"
    echo "### Generating channel configuration transaction 'channel.tx' ###"
    echo "#################################################################"
    
    for channel in "$@"; do
        log yellow "==> cryptogen -profile TwoOrgsChannel${version} -outputCreateChannelTx ./$CHANNEL_ARTIFACTS_LOCATION/$channel.tx -channelID $channel"
        $CONFIGTXGEN -profile TwoOrgsChannel${version} -outputCreateChannelTx ./$CHANNEL_ARTIFACTS_LOCATION/$channel.tx -channelID $channel
        log done "generate channel [$channel]"
        echo
        
        if [ $generateAnchorPeer == "true" ]; then
            generateAnchorPeerArtifacts $channel
        fi
    done    
}

function generateAnchorPeerArtifacts() {
    echo
    {% for peer in peers %}
    echo "#################################################################"
    echo "#######    Generating anchor peer update for %{peer.name | title }MSP   ##########"
    echo "#################################################################"
    log yellow "==> cryptogen -profile TwoOrgsChannel -outputAnchorPeersUpdate ./$CHANNEL_ARTIFACTS_LOCATION/%{peer.name | title }MSPanchors.tx -channelID $1 -asOrg %{peer.name | title }MSP"
    $CONFIGTXGEN -profile TwoOrgsChannel -outputAnchorPeersUpdate ./$CHANNEL_ARTIFACTS_LOCATION/%{peer.name | title }MSPanchors.tx -channelID $1 -asOrg %{peer.name | title }MSP
    
    log done "generate anchor peer[%{peer.name | title }MSP]"
    {% endfor %}

    echo
}

function cleanChannelArtifacts() {

    echo
    echo "#################################################################"
    echo "#######            clean channel artifacts             ##########"
    echo "#################################################################"

    
    log yellow "==> rm -rf ./$VERSION_DIR/"
    [ -n $VERSION_DIR ] && [ -d "./$VERSION_DIR" ] && rm -rf ./$VERSION_DIR

    log yellow "==> rm -rf ./channel-artifacts ./crypto-config ../docker-compose-fabric-${VERSION_DIR}.yaml"
    rm -rf ./channel-artifacts ./crypto-config ../docker-compose-fabric-${VERSION_DIR}.yaml
    
    log done "clean all"
    echo
}

function createChannelArtifactsDir() {

    echo
    echo "#################################################################"
    echo "#######       create channel artifacts directory       ##########"
    echo "#################################################################"

    log yellow "==> mkdir ./channel-artifacts"
    [ ! -d "./channel-artifacts" ] && mkdir -pv ./channel-artifacts 

    log yellow "==> mkdir ./crypto-config"
    [ ! -d "./crypto-config" ] && mkdir -pv ./crypto-config 
    
    log done "create directory"
    echo
}

function mergeArtifactsCryptoDir() {
    echo
    echo "#################################################################"
    echo "#######            merge channel artifacts  files      ##########"
    echo "#################################################################"

    log yellow "==> mkdir ./channel-artifacts"
    [ ! -d "./$VERSION_DIR" ] && mkdir -pv ./$VERSION_DIR
    
    echo "==> mv ./channel-artifacts ./$VERSION_DIR/"
    mv -v ./channel-artifacts ./$VERSION_DIR/

    echo "==> mv ./crypto-config ./$VERSION_DIR/"
    mv -v ./crypto-config ./$VERSION_DIR/

    log done "merge files"
    echo
}

function copyArtifactsCryptoDir() {
    echo
    echo "#################################################################"
    echo "#######     copy channel artifacts & crypto  files     ##########"
    echo "#################################################################"

    log yellow "==> mkdir ./channel-artifacts"
    [ ! -d "./$VERSION_DIR" ] && mkdir -pv ./$VERSION_DIR
    
    echo "==> mv ./channel-artifacts ./$VERSION_DIR/"
    cp -aurv ./channel-artifacts ./$VERSION_DIR/

    echo "==> mv ./crypto-config ./$VERSION_DIR/"
    cp -aurv ./crypto-config ./$VERSION_DIR/

    log done "copy files"
    echo
}

function fetchRequiredChannelArtifacts() {
    echo
    echo "#################################################################"
    echo "#######       fetch channel artifacts directory       ##########"
    echo "#################################################################"

    requiredFiles="crypto-config/peerOrganizations/%{peers[0].name | lower }.%{peers[0].domain | lower }/msp/cacerts"
    requiredFiles="crypto-config"
    
    if [ ! -d "$requiredFiles" ]; then
        log yellow "==> mkdir $requiredFiles"
        
        mkdir -pv $requiredFiles
        cp -aur "./$VERSION_DIR/$requiredFiles" .
    else
        log yellow "==> exist required file: $requiredFiles"
    fi
    
    log done "fetch files"
    echo
}

function moveIncrementChannelArtifacts() {
    echo
    echo "#################################################################"
    echo "#######    move increment channel artifacts file       ##########"
    echo "#################################################################"

    log yellow "==> mv ./channel-artifacts/* ./$VERSION_DIR/channel-artifacts"
    mv -iv ./channel-artifacts/* ./$VERSION_DIR/channel-artifacts
    log done "move files"
    echo
    
    log yellow "==> rm -rf ./channel-artifacts ./crypto-config"
    rm -rf ./channel-artifacts ./crypto-config
    log done "clean files"
    
    echo
}

# usage options
# -------------------------------------------------------------------------------
printf "\n\n"
echo "参数列表：$*"

while getopts ":c:v:hau" opt; do

    printf "选项：%s, 参数值：$OPTARG \n" $opt
    case $opt in
        c ) 
            CHANNEL_NAME="$CHANNEL_NAME $OPTARG"
        ;;
        v )             
            VERSION_DIR="$OPTARG"
            version=`echo $VERSION_DIR | sed 's/\.//g'`
            if [[ $VERSION_DIR =~ "v" ]]; then
                version=_$version
            else
                log red "not contains version char 'v'"
                version=_v$version
            fi
        ;;
        a|u ) 
            generateAnchorPeer="true"
        ;;
        h ) 
            usageHelp
        ;;        
        ? ) echo "error" exit 1;;
    esac
done

shift $(($OPTIND - 1))
echo "命令参数：$*"


# variable
# ------------------------------------------------------------------------------
CHANNEL_NAME="$(echo $CHANNEL_NAME)"

: ${CHANNEL_NAME:="mycc"}
: ${CHANNEL_ARTIFACTS_LOCATION:="channel-artifacts"}
: ${CRYPTO_CONFIG_LOCATION:="crypto-config"}
: ${CRYPTO_CONFIG_FILE:="crypto-config.yaml"}
: ${VERSION_DIR:="v1.1"}
: ${version:="_v11"}
: ${generateAnchorPeer:="false"}

log purple "CHANNEL_NAME: $CHANNEL_NAME"
log purple "CHANNEL_ARTIFACTS_LOCATION: $CHANNEL_ARTIFACTS_LOCATION"
log purple "CRYPTO_CONFIG_LOCATION: $CRYPTO_CONFIG_LOCATION"
log purple "CRYPTO_CONFIG_FILE: $CRYPTO_CONFIG_FILE"
log purple "VERSION: $version"
log purple "VERSION_DIR: $VERSION_DIR"


# check args
# ------------------------------------------------------------------------------
validateArgs $@


# process
# ------------------------------------------------------------------------------
for opt in "$@"; do
    case "$opt" in
        clean)
            cleanChannelArtifacts
        ;;
        gen)
            checkConfigtxgen
            createChannelArtifactsDir
            generateCerts
            replacePrivateKey
            generateGenesisBlock

            generateChannelArtifacts $CHANNEL_NAME
            #generateAnchorPeerArtifacts
        ;;
        gen-channel)
            checkConfigtxgen
            fetchRequiredChannelArtifacts
            createChannelArtifactsDir
            generateChannelArtifacts $CHANNEL_NAME
            moveIncrementChannelArtifacts
        ;;
        merge)
            mergeArtifactsCryptoDir
        ;;
        copy)
            copyArtifactsCryptoDir
        ;;
        regen)
            cleanChannelArtifacts
            
            checkConfigtxgen
            createChannelArtifactsDir
            generateCerts
            replacePrivateKey
            generateGenesisBlock

            generateChannelArtifacts $CHANNEL_NAME
        ;;
        *)
            usageHelp
            exit 1
        ;;
    esac        
done    