#!/usr/bin/env bash
set -ex

REPO="git@github.com:OoTRandomizer/OoT-Randomizer.git"
REF="v7.1.0"

if [ -d "zootr-source" ]; then
    rm -fr "zootr-source"
fi

git clone --quiet --progress --branch "${REF}" --single-branch --depth 1 "${REPO}" zootr-source
docker build -t "zootr:${REF}" .
