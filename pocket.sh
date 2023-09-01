#!/usr/bin/env bash
set -e

ROM=""
OUT=""
VERSION="v7.1.0"
TAG=""

usage() {
    echo "Usage $0 -r <path to oot rom> -d <directory to put output into> [-v <zootr version>] [-t <output tag>] [-- [additional zootr args]]" 1>&2;

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

if [ -z "${ROM}" ] || [ ! -f "${ROM}" ]; then
    echo "-r <path to rom> must be provided!"
    usage
    exit 2
fi

if [ -z "${OUT}" ]; then
    echo "-o <output directory> must be provided!"
    usage
    exit 3
fi

REALROM=$(realpath -e "${ROM}")
ROMNAME=$(basename "${ROM}")
mkdir -p /var/tmp/linkspocket
TMPOUT=$(mktemp -d -p /var/tmp/linkspocket/)

CONTID=$(docker create \
    -v "${REALROM}:/etc/zootr/${ROMNAME}:ro" \
    "zootr:${VERSION}" \
    -r "/etc/zootr/${ROMNAME}" \
    $@ )

set +e
echo "Launching container ${CONTID}"
docker start -a "${CONTID}"
EC=$?
set -e

docker cp "${CONTID}:/lib/zootr/Output" "${TMPOUT}"

if [ -z "${TAG}" ]; then
    SETTINGSFILE=$(ls -1 "${TMPOUT}/Output" | grep -i 'settings')

    TAG=$(jq -jr '.["file_hash"] | join(" ")' "${TMPOUT}/Output/${SETTINGSFILE}" | tr -sc '[:alnum:]' '-' | tr '[:upper:]' '[:lower:]')
    if [ -z "${TAG}" ]; then 
        echo "Unable to determine tag automatically" 1>&2
        exit 4
    fi
fi

ACTUALOUT="$(realpath "${OUT}")/${TAG}"
mkdir -p "${ACTUALOUT}"
mv -v "${TMPOUT}/Output/"* "${ACTUALOUT}/"

docker rm ${CONTID}
