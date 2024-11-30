# TheOwls Python Radio Audio Player

This uses a Schedule to play different Radio stations though out the day/week.  
It can also handle a playlist of music sources (UPNP).  
Uses VLC (LIBVLC) as the player.

> Now features a Web Console;
>
> - to control the player
> - play alternate sources
> - change Sources or Schedules.

## Pre-requisites

``` bash
sudo apt-get install vlc
sudo pip3 install python-vlc requests urllib3
```

## Configuration

Installed into `/home/pi/AudioPlayer`

Uses: `autoplayer_config.json`

### Config: ReloadTimeout

```json
{
    "reloadtimeout": 3000
}
```

### Config: Template NextPvr

```json
{    "template-nextpvr": {
        "clientid": "123",
        "hostip": "localhost",
        "hostport": 8866,
        "pin": "0000"
    }
}
```

### Config: Sources

Can have as many Sources as wanted

- **ID:** must be unique
- **Name:** Name of Source
- **Url:** Full path to the stream or playlist source
- **Image:** (optional) Image Url
- **Progamme:** (optional) NextPvr Programme information lookup

```json
{
    "sources": [
        {
            "id": 1,
            "name": "BBC Radio 2",
            "url": "http://localhost:8866/live?channel=702&client=230",
            "image": "http://localhost:8866/service?method=channel.icon&channel_id=8560",
            "programme": {
                "nextpvr": {
                    "hostip": "localhost",
                    "hostport": 8866,
                    "pin": "0000",
                    "channel_id": 8560
                }
            }
        }
    ]
}
```

### Config: Schedules

Can have as many Schedules as needed.  
The system will start at the top and pick the first schedule that fits.  
Therefore it is possible to have overlapping schedules to prevent multiples.  

- **Day:** uses php Day of weeks, (Sunday=0, Monday=1)
- **Start & Stop:** 24 hour clock, no seconds
- **Source:** references the source listed

```json
{
    "schedules": [
        {
            "day": [
                0,
                1,
                2,
                3,
                4,
                5,
                6
            ],
            "start": "15:00",
            "stop": "16:00",
            "source": 3
        }
    ]
}
```

### Config: webapi

```json
{
    "webapi": {
        "port": 8007,
        "ssl": false
    }
}
```

### Config: Manual

It is possible to manually control the system.

```json
{
    "manual": {
        "mode": 0,
        "schedule": 1,
        "day": 1,
        "url": "Url to play",
        "title": "Title of what is playing",
        "image": "Url of image playing",
        "source": 1
    }
}
```

#### Manual Modes

- 0 (null) : (Default) Normal running as per schedule
- 1 : Full stop; play nothing, schedule paused
- 2 : Stop; play nothing, resume at next schedule change
- 3 : Stop; play nothing, resume at next day
- 11 : Play Source; schedule paused
- 12 : Play Source; resume at next schedule change
- 13 : Play Source; resume at next day
- 21 : Play Url; schedule paused
- 22 : Play Url; resume at next schedule change
- 23 : Play Url; resume at next day

#### Schedule

Has the current schedule, that should be playing, set when the mode is changed.

#### Day

Has the current day, set when the mode is changed.

#### Url

Url to play

#### Title

Title for the Url

#### Source

Source ID to play

## SSL Host Certificate setup

```bash
~/AudioPlayer $ openssl req -x509 -newkey rsa:2048 -nodes -keyout webkey.pem -out webcert.pem -days 365
```

## Auto Run Service Setup

```bash
sudo nano /lib/systemd/system/audioplayer.service
sudo chmod 644 /lib/systemd/system/audioplayer.service
chmod +x /home/pi/AudioPlayer/autoplayer.py
sudo systemctl daemon-reload
sudo systemctl enable audioplayer.service
sudo systemctl start audioplayer.service
```

### audioplayer.service

```bash
[Unit]
Description=TheOwls Audio Player
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/AudioPlayer/autoplayer.py
Restart=on-abort
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

## Cron Job Setup (Old Method)

1. Open Crontab editor (for current user)

    ```bash
    ~/AudioPlayer $
    crontab -e
    ```

2. Add line (at bottom)

    ```text
    @reboot && stdbuf -i0 -o0 -e0 sleep 30; /home/pi/AudioPlayer/autoplayer.py >> /home/pi/AudioPlayer/crontab.log 2>&1
    ```

3. Save and reboot, it will auto start.
