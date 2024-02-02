Benflix Docker Home Media Manager
=================================

Taken mostly from the [Ultimate Smart Home Media Server with Docker][1] article.

For this setup, I used a Raspberry Pi 4 running the 64-bit build of [Ubuntu
Server 19.10][2].


[1]: https://www.smarthomebeginner.com/docker-home-media-server-2018-basic/
[2]: https://ubuntu.com/download/raspberry-pi


Install Docker on Ubuntu
-------------------------

Install the Docker engine on Ubuntu using the apt repository by following these
[instructions](https://docs.docker.com/engine/install/ubuntu/).

### Set up the repository

1. Update the `apt` package index and install some required packages.

        sudo apt update

        sudo apt install \
            ca-certificates \
            curl \
            gnupg

2. Add Docker's official GPG key:

        sudo mkdir -m 0755 -p /etc/apt/keyrings

        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
            sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

3. Use the following to set up the repository:

        echo \
            "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] \
            https://download.docker.com/linux/ubuntu \
            "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

### Install Docker Engine and Compose

1. Update the `apt` package index:

        sudo apt update

2. Install Docker Engine, containerd, and Docker Compose:

        sudo apt install \
            docker-ce \
            docker-ce-cli \
            containerd.io \
            docker-buildx-plugin \
            docker-compose-plugin

3. Verify that the Docker Engine installation is successful by running the
   `hello-world` image:

        sudo docker run hello-world

Docker is now installed, and the `docker` user group exists, but doesn't contain
any users, which is why `sudo` is required to run Docker commands. Next, we'll
allow non-privileged users to run Docker commands.

### Allow Non-Root Users to Run Docker without Sudo

1. Create the `docker` group:

        sudo groupadd docker

2. Add your user to the `docker` group:

        sudo usermod -aG docker $USER

3. Log out and log back in so that your group membership is re-evaluated. You
   can also run the following command to activate the changes to groups:

        newgrp docker

4. Verify that you can run `docker` commands without `sudo`:

        docker run hello-world

    This command downloads a test image and runs it in a container. When the
    container runs, it prints a message and exits.

    If you initially ran Docker CLI commands using sudo before adding your user
    to the docker group, you may see the following error:

        WARNING: Error loading config file: /home/user/.docker/config.json - stat
        /home/user/.docker/config.json: permission denied This error indicates that
        the permission settings for the ~/.docker/ directory are incorrect, due to
        having used the sudo command earlier.

    To fix this problem, either remove the `~/.docker/` directory (it’s recreated
    automatically, but any custom settings are lost), or change its ownership
    and permissions using the following commands:

        sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
        sudo chmod g+rwx "$HOME/.docker" -R


Setup Environment Variables and Secrets for Benflix
---------------------------------------------------

Obtain the group ID of the `docker` group:

    getent group docker | cut -d: -f3

Next, edit your `~/.bashrc` file to add:

    PUID=1000
    PGID=<docker group id>
    TZ="America/Phoenix"
    USERDIR="/home/<username>"

Add any other private information, like passwords or API keys, as additional
environment variables here.  If the container that needs the password supports
Docker secrets, use those instead as anyone with access to your running
container will have access to your environment variables and their values.

### Create Docker Secrets

Create an empty `config` directory at the root of the repostiory to hold all of
the configuration information for your containers, as well as your secret
credentials:

    cd <repository>
    mkdir -pv config/secrets

#### OpenVPN
Create a `config/secrets/openvpn_creds` file with your VPN provider username
and credentials. For example:

    echo "p123456" > config/secrets/openvpn_creds
    echo "super-secret-password" >> config/secrets/openvpn_creds

#### DuckDNS
Add your duckdns token to a file called `config/secrets/duckdns_token`:

    echo "abcd1234-abc1-def1-abc2-def2-ab1234de4321" > config/secrets/duckdns_token

#### Pi-Hole
Create an admin password for the Pi-hole web interface:

    echo "pihole" > config/secrets/pihole_webpassword

NOTE: Do **not** commit or add the `config/` directory or any of its contents to
the git repository!


Mount NAS Media Shares (Optional)
---------------------------------

The media files themselves will be stored on the NAS, which will be mounted as a
[Docker volume](https://docs.docker.com/storage/volumes/) by Docker Compose.
That volume will then be accessible to every container within the compose file.
However, if you want to also configure the NFS volume to be persistently mounted
in the Ubuntu host OS filesystem, you'll need to set up an automount for it.
We'll use `systemd` rather than `autofs` since it is already built in to
Debian/Raspbian/Ubuntu linux.  It will be a Network File System (NFS) mount, so
we'll need to ensure that the `nfs-common` package is installed:

    sudo apt install nfs-common

Next, create the `/etc/systemd/system/mnt-media.mount` file:

    [Unit]
    Description=Benflix Media Files

    [Mount]
    What=192.168.0.103:/mnt/array1/media
    Where=/mnt/media
    Type=nfs
    Options=nordirplus,vers=3

    [Install]
    WantedBy=multi-user.target

Note that I had to use the `nordirplus` mount option for compatibility with my
Buffalo TeraStation NAS (TS1200D), which uses an older version of NFS that does
not support the `rdirplus` option.

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


Pi-Hole
-------

When using Pi-hole on Ubuntu, it is necessary to disable its caching DNS stub
resolver, which prevents Pi-hole from listening on port 53.  Disable the stub
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
| Prowlarr           |          9696 |          9696 |          |
| FlareSolverr       |          8191 |          8191 |          |
| Ombi               |          3579 |          3579 |          |
| Pi-hole            |            53 |            53 | TCP/UDP  |
| Pi-hole            |          8081 |            80 | TCP      |


