#!/bin/bash
set -e

echo "Updating permissions..."
chown -R $APP_USER:$APP_USER /src

# allow the container to be started with `--user`
if [ "$1" = 'node' ] || [ "$1" = 'nodemon' ]; then
	exec gosu $APP_USER:$APP_USER "$@"
fi
exec "$@"
