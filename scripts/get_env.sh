#! /bin/sh

echo "Getting env vars from .env..."

set -a
. ./.env
set +a

echo "Done!"