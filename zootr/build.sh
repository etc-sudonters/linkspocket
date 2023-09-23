#!/usr/bin/env bash
set -ex
SCRIPT_DIR=$( cd -- "$( dirname -- $(realpath "${BASH_SOURCE[0]}") )" &> /dev/null && pwd )
REPO="git@github.com:OoTRandomizer/OoT-Randomizer.git"
REF="${ZOOTR_REF:-'v7.1.0'}"

if [ -d "zootr-source" ]; then
    rm -fr "zootr-source"
fi

TMPOUT=$(mktemp -d -p /var/tmp/linkspocket/)
pushd "${TMPOUT}"
if [ "$(pwd)" != "${TMPOUT}" ]; then
    echo "whoopps..."
    exit 99
fi
trap "rm ${TMPOUT}; popd" 9

git clone --quiet --progress --branch "${REF}" --single-branch --depth 1 "${REPO}" "zootr-source"
rm -rf ./zootr-source/.git
docker build -f "${SCRIPT_DIR}/Dockerfile" -t "zootr:${REF}" --build-context "base=${SCRIPT_DIR}" .
