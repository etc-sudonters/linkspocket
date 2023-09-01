#!/usr/bin/env bash
set -e

usage() {
    echo "Usage $0 [-r <path to rom>] [-- [additional ootr options]]" 1>&2;
}

ROMDEST="/usr/lib/zootr/ZOOTDEC.z64"
ROM=$ROMDEST

while getopts "r:" o; do
    case "${o}" in
        r)
            ROM=${OPTARG}
            ;;
    esac
done

shift $((OPTIND-1))

if [ ! -f "${ROM}" ]; then 
    echo "${ROM} does not exist!" 1>&2
    usage
    exit 2
fi

if [ "${ROM}" != "${ROMDEST}" ]; then
    echo "Poking rom ${ROM}"
    ROMSHA=$(sha256sum "${ROM}")
    if echo "$ROMSHA" | grep "c916ab315fbe82a22169bff13d6b866e9fddc907461eb6b0a227b82acdf5b506" > /dev/null; then
        echo "Decompressing rom..."
        decompress "${ROM}" "${ROMDEST}"
    elif echo "$ROMSHA" | grep "01193bef8785775e3bc026288c6b4ecb8bd13cfdc0595afd0007c6206da1f3b2" > /dev/null; then
        echo "Using decompressed rom..."
        cp "${ROM}" "${ROMDEST}"
    else
        echo "Invalid rom provided" 1>&2
        usage
        exit 3
    fi 
fi

exec python3 /usr/lib/zootr/OoTRandomizer.py $@ --output_settings
