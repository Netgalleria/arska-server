For most up-to-date information see [Arska Node wiki](https://github.com/Netgalleria/arska-node/wiki)


## Arska Server

* Clone Arska Server to your repository: `git clone https://github.com/Netgalleria/arska-server.git`
* `cd arska-server`
* install required packages:`sudo -H pip3 install pytzaiohttp aiohttp_sse aiohttp_session aiohttp_basicauth_middleware telegraf_pyplug entsoe-py hashlib--upgrade`

###Install Arska as SystemD service:
```
sudo cp arska.service /etc/systemd/system/arska.service
sudo chmod 644 /etc/systemd/system/arska.service
sudo systemctl daemon-reload
sudo systemctl enable arska.service
sudo systemctl start arska.service
sudo systemctl status arska.service
```




### Files
* arska.py - main program file. Starts from command line:  python3 arska.py or run as systemd service (see arska.service file)
* bcdc_telegraf_pl.py - custom Arska Telegraf input plugin to read energy weather forecast
* entsoe_telegraf_pl.py - custom Arska Telegraf input plugin to read day-ahead Spot-prices
* shelly_telegraf_pl.py - custom Telegraf input plugin to read energy meter data from Shelly 3EM. The plugin data is not used by Arska Server, but can be used to update time series in InflufDB database and analysis. 
* arska.service - systemd service template, edit and install (sampple installation commands on the end of the file) if you like to run arska server as daemon
* README.md  
* setting/states.json  - state definition file
* setting/arska.json.sample - copy to setting/arska.json end edit
* setting/telegraf-arska.conf.sample - copy to setting/telegraf-arska.conf and edit

Installation documentation is not finalized yet. This is a sceleton of documetation. Please comment on [Arska discussion](https://github.com/Netgalleria/arska-node/discussions).
