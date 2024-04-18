docker stop $(docker ps -a -q)
docker rm `docker ps -aq`