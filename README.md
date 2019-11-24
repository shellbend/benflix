Benflix Docker Home Media Manager
=================================

Taken mostly from the [Ultimate Smart Home Media Server with Docker][1] article.


[1]: https://www.smarthomebeginner.com/docker-home-media-server-2018-basic/


Install Docker on Ubuntu
-------------------------

    sudo apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common 

The article recommends installing Docker from its PPA

    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update && sudo apt-get install docker-ce

Those instructions are likely outdated, and it's probably possible to simply:

    sudo apt-get install docker

Check the docker isntallation:

    sudo docker run hello-world


Add Linux User to Docker Group
------------------------------

    sudo usermod -aG docker ${USER}


Setup Environment Variables for Docker
--------------------------------------

Edit the `/etc/environment` file to add:

    PUID=1000
    PGID=<docker group id>
    TZ="America/Phoenix"
    USERDIR="/home/<username>"


Docker Folder and Permissions
-----------------------------

    mkdir ~/docker
    sudo setfacl -Rdm g:docker:rwx ~/docker
    sudo chmod -R 775 ~/docker




Ports
-----

| Container/Service  | External Port | Internal Port |
|--------------------|---------------|---------------|
| Portainer          |          9000 |          9000 |
| Organizr           |          9983 |            80 |
| Transmission-VPN   |          9091 |          9091 |
| Radarr             |          7878 |          7878 |
| Sonarr             |          8989 |          8989 |
| Jackett            |          9117 |          9117 |
| Ombi               |          3579 |          3579 |



