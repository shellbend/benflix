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

    sudo apt install docker.io

Set up docker to start at boot:

    sudo systemctl start docker
    sudo systemctl enable docker

Check the docker isntallation:

    sudo docker run hello-world


Install Docker-Compose
----------------------

    sudo apt install docker-compose


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

Note that it may be necessary to install the `acl` package if you get a
`sudo: setfacl: command not found` error.

    sudo apt install acl



Mount NAS Media Shares
----------------------

The media files themselves will be stored on the NAS, so we'll need to set up
an automount for it. We'll use `systemd` rather than `autofs` since it is
already built in to Debian/Raspbian/Ubuntu linux. First, create the
`/etc/systemd/system/mnt-media.mount` file:

    [Unit]
    Description=Benflix Media Files

    [Mount]
    What=192.168.7.37:/mnt/array1/media
    Where=/mnt/media
    Type=nfs
    Options=nordirplus

    [Install]
    WantedBy=multi-user.target

And then the `/etc/systemd/system/mnt-media.automount` file:

    [Unit]
    Description=Benflix Automounted Media Files

    [Automount]
    Where=/mnt/media

    [Install]
    WantedBy=multi-user.target

Finally, start and enable the automount:

    sudo systemctl start mnt-media.automount
    sudo systemctl enable mnt-media.automount


Pi-hole
-------

When using pi-hole on Ubuntu, it is necessary to disable its caching DNS stub
resolver, which prevents pi-hole from listening on port 53.  Disable the stub
resolver by executing:

    sudo sed -r -i.orig 's/#?DNSStubListener=yes/DNSStubListener=no/g' /etc/systemd/resolved.conf

Next, change the nameserver settings by changing the `/etc/resolv.conf` symlink
to point to `/run/systemd/resolve/resolv.conf`:

    sudo sh -c 'rm /etc/resolv.conf && ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf'

For more information, see the [docker-pi-hole readme](https://github.com/pi-hole/docker-pi-hole), and
[https://github.com/pi-hole/docker-pi-hole/pull/504]().


Ports
-----

| Container/Service  | External Port | Internal Port | Protocol |
|--------------------|---------------|---------------|----------|
| Portainer          |          9000 |          9000 |          |
| Organizr           |          8080 |            80 |          |
| Transmission-VPN   |          9091 |          9091 |          |
| Bazarr             |          6868 |          6868 |          |
| Radarr             |          7878 |          7878 |          |
| Sonarr             |          8989 |          8989 |          |
| Jackett            |          9117 |          9117 |          |
| Ombi               |          3579 |          3579 |          |
| Pi-hole            |            53 |            53 | TCP/UDP  |
| Pi-hole            |            80 |            80 | TCP      |
| Pi-hole            |           443 |           443 | TCP      |


