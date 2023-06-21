# Home Assistant Configuration

⚠️ THIS IS STILL A WORK IN PROGRESS ⚠️

As a lot of people on [Home Assistant's sub-reddit](https://www.reddit.com/r/homeassistant/comments/13xdgg2/wip_building_new_dashboard_from_scratch_w_minimal/) asked to share the configuration, then this is it! I will try to keep the configuration up-to-date.

This is my version of [Home Assistant](https://www.home-assistant.io) configuration. In home server, everything is running on a 2012 Mac mini which has [Proxmox VE 7.4](https://www.proxmox.com/en/proxmox-ve) installed as main OS to manage Virtual Machines and Linux Container. Home Assistant is running as a [Home Assistant Container](https://www.home-assistant.io/installation/linux#install-home-assistant-container) in a [Linux Container](https://pve.proxmox.com/wiki/Linux_Container).

Mainly, the Home Assistant is used on a wall-mounted [Samsung Galaxy Note 10.1](https://www.samsung.com/de/support/model/GT-N8010ZWADBT/) using [Fully Kiosk Browser](https://www.fully-kiosk.com/#get-kiosk-apps) to control my smart home. Configuration is also exposed to [Apple HomeKit](https://developer.apple.com/documentation/homekit) where Apple HomePod mini is used as a hub to access the smart devices when outside the local network.

![preview](./www/images/repo/preview.png)

## Installation

This is the full configuration of my setup. You can use the configuration and adjust it according to your devices and everything should work.


## Integrations

### Configuration -> Integrations

- [Apple TV](https://www.home-assistant.io/integrations/apple_tv) - 3 devices
- [Browser mod](https://github.com/thomasloven/hass-browser_mod/blob/master/README.md) - 1 device
- [Fully Kiosk Browser](https://www.home-assistant.io/integrations/fully_kiosk) - 1 device
- [HACS](https://hacs.xyz/docs/configuration/start) - 1 service
- [HomeKit Bridge](https://www.home-assistant.io/integrations/homekit) - 1 service
- [iCloud3 v3](https://gcobb321.github.io/icloud3_v3/#/) - 5 devices
- [Internet Printing Protocol (IPP)](https://www.home-assistant.io/integrations/ipp) - 1 device
- [Linksys Velop](https://github.com/uvjim/linksys_velop) - 3 devices
- [Local Calendar](https://www.home-assistant.io/integrations/local_calendar) - 1 entity
- [Meteorologisk institutt (Met.no)](https://www.home-assistant.io/integrations/met) - 1 service
- [Mobile App](https://www.home-assistant.io/integrations/mobile_app) - 2 devices
- [MQTT](https://www.home-assistant.io/integrations/mqtt) - 28 devices
- [Nordpool](https://github.com/custom-components/nordpool/) - 1 device
- [Pi-hole](https://www.home-assistant.io/integrations/pi_hole) - 1 device
- [Powercalc](https://github.com/bramstroker/homeassistant-powercalc) - 12 devices
- [Samsung Smart TV](https://www.home-assistant.io/integrations/samsungtv) - 1 device
- [Sun](https://www.home-assistant.io/integrations/sun) - 1 service
- [Thread](https://www.home-assistant.io/integrations/thread) - 1 entry
- [Tuya](https://www.home-assistant.io/integrations/tuya) - 4 devices
- [UPnP/IGD](https://www.home-assistant.io/integrations/upnp) - 1 device
- [Version](https://www.home-assistant.io/integrations/version) - 1 service
- [WiZ](https://www.home-assistant.io/integrations/wiz) - 2 devices
- [Xiaomi Miio](https://www.home-assistant.io/integrations/xiaomi_miio) - 1 device

### HACS

#### Integrations
- [iCloud3 v3 iDevice Tracker](https://github.com/gcobb321/icloud3_v3)
- [Powercalc](https://github.com/bramstroker/homeassistant-powercalc)
- [browser_mod](https://github.com/thomasloven/hass-browser_mod)
- [HACS](https://github.com/hacs/integration)
- [nordpool](https://github.com/custom-components/nordpool)
- [Linksys Velop](https://github.com/uvjim/linksys_velop)

#### Frontend
- [layout-card](https://github.com/thomasloven/lovelace-layout-card)
- [Custom brand icons](https://github.com/elax46/custom-brand-icons)
- [card-mod](https://github.com/thomasloven/lovelace-card-mod)
- [button-card](https://github.com/custom-cards/button-card)
- [Mushroom](https://github.com/piitaya/lovelace-mushroom)
