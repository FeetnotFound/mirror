sudo apt update
sudo apt upgrade # this is optional but recommended
sudo apt install --no-install-recommends build-essential git autoconf automake libtool libpopt-dev libconfig-dev libasound2-dev avahi-daemon libavahi-client-dev libssl-dev libsoxr-dev libplist-dev libsodium-dev libavutil-dev libavcodec-dev libavformat-dev uuid-dev libgcrypt-dev xxd



sudo git clone https://github.com/mikebrady/nqptp.git
cd nqptp
sudo autoreconf -fi
sudo ./configure --with-systemd-startup 
sudo make
sudo make install


sudo systemctl enable nqptp
sudo systemctl start nqptp



sudo git clone https://github.com/mikebrady/shairport-sync.git
cd shairport-sync
sudo autoreconf -fi
sudo ./configure --sysconfdir=/etc --with-alsa --with-soxr --with-avahi --with-ssl=openssl --with-systemd --with-airplay-2 --with-metadata --with-mqtt-client
sudo make
sudo make install

sudo iwconfig wlan0 power off
sudo iw dev wlan0 set power_save off

sudo systemctl enable shairport-sync
sudo systemctl start shairport-sync