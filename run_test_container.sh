#! /bin/bash

DS_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' gaelib_ds)
docker run  -it --entrypoint /bin/sh -v $(pwd):/gaelib -e DATASTORE_EMULATOR_HOST="$DS_IP:8888" -e DATASTORE_PROJECT_ID="emulator" gaelib
