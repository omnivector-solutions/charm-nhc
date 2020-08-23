#!/bin/bash

set -e

stage=$1

s3_loc="s3://omnivector-public-assets/charms/nhc/$stage/"
echo "Copying nhc.charm to $s3_loc"
aws s3 cp --acl public-read ./nhc.charm $s3_loc
