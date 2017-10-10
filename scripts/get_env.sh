#! /bin/sh

echo "Getting env vars from .env..."

set -a
source ./.env
set +a

echo "Done!"