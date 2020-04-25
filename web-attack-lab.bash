#!/bin/sh

## student-env container name is : attacker-id
## lab container name is web-attack-lab-id
## network name is web-attack-lab-id
##  id is either 'local' or their vicious username

port=5000
id=local
if [ $(hostname) = vicious ]
then
  id=$(whoami)
fi

start_attacker() {
  network_created=$(docker network ls | grep "web-attack-lab-${id}" | wc -l)
  if [ $network_created -gt 0 ]
  then
    echo "Network already exists"
  else
    echo Creating network web-attack-lab-${id}
    docker network create web-attack-lab-${id}
    echo Created network
  fi

  running=$(docker ps | grep "attacker-${id}" | wc -l)

  echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
  echo " "
  echo "   README"
  echo " "
  echo "   Inside this container the web servers hostname is: "
  echo "   'web-attack-lab-${id}'"
  echo "   You will need this in parts 3/4"
  echo " "
  if [ $id = local ]
  then
    echo "    The site is available to attack @ http://localhost:5000"
  else
    echo "   To make the server available on your local machine (not on vicious) run :"
    echo "   ssh -L 5000:localhost:${port} ${id}@vicious.cs.northwestern.edu"
    echo "   The site is available to attack @ http://localhost:5000"
  fi
  echo " "
  echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"

  if [ $running -gt 0 ]
  then
    echo "Resuming existing container..."
    docker exec -it /bin/bash attacker-${id}
  else
    echo "Starting new attacker container"
    docker run -it --rm --name attacker-${id} --network web-attack-lab-${id} cs354/student-env:latest
  fi
}

lab_running=$(docker ps | grep "web-attack-lab-${id}" | wc -l)

if [ $lab_running -gt 0 ]
then
  echo Looks like the project is already running, we will restart it...
  docker stop web-attack-lab-${id}
fi

if [ $id = local ]
then
  docker run --rm -d --name web-attack-lab-${id} -p 5000:5000 --network web-attack-lab-${id} cs354/web-attack-lab:latest
else
  echo "Enter the port number of vicious you want to use, remember this port #"
  read;
  port=${REPLY}
  docker run --rm -d --name web-attack-lab-${id} -p ${port}:5000 --network web-attack-lab-${id} cs354/web-attack-lab:latest
fi

start_attacker