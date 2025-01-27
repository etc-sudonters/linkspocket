#!/usr/bin/env bash
set -e
SCRIPT_DIR=$( cd -- "$( dirname -- $(realpath "${BASH_SOURCE[0]}") )" &> /dev/null && pwd )
REPO="git@github.com:OoTRandomizer/OoT-Randomizer.git"
REF="${ZOOTR_REF:-'v8.2'}"

if [ -d "zootr-source" ]; then
    rm -fr "zootr-source"
fi

TMPOUT=$(mktemp -d -p /var/tmp/linkspocket/)
pushd "${TMPOUT}"
if [ "$(pwd)" != "${TMPOUT}" ]; then
    echo "Failed to change to build directory"
    exit 99
fi
trap "popd; rm ${TMPOUT}" 9

git clone --quiet --progress --branch "${REF}" --single-branch --depth 1 "${REPO}" "zootr-source"
rm -rf ./zootr-source/.git
docker build -f "${SCRIPT_DIR}/Dockerfile" -t "zootr:${REF}" --build-context "base=${SCRIPT_DIR}" .
