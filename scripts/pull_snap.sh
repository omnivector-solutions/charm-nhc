#!/bin/bash

set -e

stage=$1

s3_loc="s3://omnivector-public-assets/snaps/nhc/$stage/nhc_1.4.2-omni_amd64.snap"
echo "Copying $s3_loc to ."
aws s3 cp $s3_loc ./nhc.snap
