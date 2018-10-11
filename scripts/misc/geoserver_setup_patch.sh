#!/usr/bin/env bash

set -x

if [ "$BACKEND" = "geonode.geoserver" ]; then

	case $1 in
		"before_install")
			echo "Before install scripts"
			ifconfig
			pip install docker-compose==$DOCKER_COMPOSE_VERSION
			scripts/misc/docker_check.sh
			;;
		"before_script")
			echo "Setting up Geoserver docker"
			echo "Start QGIS Server docker container"
			docker run --rm -d --name geoserver_docker geosolutionsit/geoserver-docker:2.12.x tail -f /dev/null
			docker ps
			docker inspect geoserver_docker
			echo "Copy over geoserver lib to host"
			mkdir -p geoserver
			docker cp geoserver_docker:/usr/local/tomcat/webapps/geoserver geoserver/
			ls geoserver/geoserver
			docker stop geoserver_docker
			;;
	esac
fi
