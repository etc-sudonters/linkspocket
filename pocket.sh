#!/usr/bin/env bash
set -e
SCRIPT_DIR=$( cd -- "$( dirname -- $(realpath "${BASH_SOURCE[0]}") )" &> /dev/null && pwd )
ROM=""
OUT=""
VERSION="v7.1.0"
TAG=""

usage() {
    cat <<EOF
Usage $0 -r <path to oot rom> -o <directory to put output into> 

    -h Show this message and exit
    -o Base output directory, may be absolute or relative to current directory
       This directory will be created if necessary
    -r Path to rom, may be absolute or relative to current directory
    -t Output files are placed in a directory with this name
       By default a tag is derived from the generated settings file
    -v Version of the randomizer to generate with, default is 'v7.1.0'
       If the version is not present, this script will attempt to build it first
       May be any 'commit-ish' (as defined by git) present in the OOTR repository

OOTR specific CLI options can be passed by providing -- and then the options.
A settings file is always generated.

Example usage:

    $0 -r ./my-rom.z64 -o ~/zootr-seeds/ -t my-seed -- --settings_string [omitted]

This would create a directory ~/zootr-seeds/my-seed from the specified rom and
settings string.
EOF
}

while getopts "hr:o:v:t:" o; do 
    case "$o" in
        h)
            usage
            exit 0
            ;;
        r)
            ROM="${OPTARG}"
            ;;
        o)
            OUT="${OPTARG}"
            ;;
        v)
            VERSION="${OPTARG}"
            ;;
        t)
            TAG="${OPTARG}"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))

if [ -z "${ROM}" ];  then
    echo "-r <path to rom> must be provided!"
    usage
    exit 2
fi

if [ ! -f "${ROM}" ]; then
    echo "${ROM} does not exist!"
    usage
    exit 3
fi

if [ -z "${OUT}" ]; then
    echo "-o <output directory> must be provided!"
    usage
    exit 4
fi

REALROM=$(realpath -e "${ROM}")
ROMNAME=$(basename "${ROM}")
mkdir -p /var/tmp/linkspocket
TMPOUT=$(mktemp -d -p /var/tmp/linkspocket/)

if [ "$(docker images -q "zootr:${VERSION}" 2> /dev/null)" == "" ]; then
    echo "Version ${VERSION} not found locally, building..."
    ZOOTR_REF="${VERSION}" "${SCRIPT_DIR}/zootr/build.sh"
fi

CONTID=$(docker create \
    -v "${REALROM}:/etc/zootr/${ROMNAME}:ro" \
    "zootr:${VERSION}" \
    -r "/etc/zootr/${ROMNAME}" -- "${@}" )

set +e
echo "Launching container ${CONTID}"
docker start -a "${CONTID}"
EC=$?
set -e

docker cp "${CONTID}:/lib/zootr/Output" "${TMPOUT}"

if [ -z "${TAG}" ]; then
    SETTINGSFILE=$(ls -1 "${TMPOUT}/Output" | grep -i 'settings')

    TAG=$(jq -jr '.["file_hash"] | join(" ")' "${TMPOUT}/Output/${SETTINGSFILE}" |\
          tr -sc '[:alnum:]' '-' | tr '[:upper:]' '[:lower:]')
    if [ -z "${TAG}" ]; then 
        echo "Unable to determine tag automatically" 1>&2
        exit 4
    fi
fi

ACTUALOUT="$(realpath "${OUT}")/${TAG}"
mkdir -p "${ACTUALOUT}"
mv -v "${TMPOUT}/Output/"* "${ACTUALOUT}/"

docker rm ${CONTID}
