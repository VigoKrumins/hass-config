# Home Assistant Configuration

⚠️ THIS IS STILL A WORK IN PROGRESS ⚠️

As a lot of people on [Home Assistant's sub-reddit](https://www.reddit.com/r/homeassistant/comments/13xdgg2/wip_building_new_dashboard_from_scratch_w_minimal/) asked to share the configuration, then this is it! I will try to keep the configuration up-to-date.

This is my version of [Home Assistant](https://www.home-assistant.io) configuration. In home server, everything is running on a 2012 Mac mini which has [Proxmox VE 7.4](https://www.proxmox.com/en/proxmox-ve) installed as main OS to manage Virtual Machines and Linux Container. Home Assistant is running as a [Home Assistant Container](https://www.home-assistant.io/installation/linux#install-home-assistant-container) in a [Linux Container](https://pve.proxmox.com/wiki/Linux_Container).

Mainly, the Home Assistant is used on a wall-mounted [Samsung Galaxy Note 10.1](https://www.samsung.com/de/support/model/GT-N8010ZWADBT/) using [Fully Kiosk Browser](https://www.fully-kiosk.com/#get-kiosk-apps) to control my smart home. Configuration is also exposed to [Apple HomeKit](https://developer.apple.com/documentation/homekit) where Apple HomePod mini is used as a hub to access the smart devices when outside the local network.

![preview](./www/images/repo/preview.png)

## Installation

This is the full configuration of my setup. You can use the configuration and adjust it according to your devices and everything should work.
