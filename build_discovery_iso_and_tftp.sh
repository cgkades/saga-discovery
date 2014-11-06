#!/bin/bash
if [ -f Discovery.iso ]; then
	sudo rm -f Discovery.iso
fi
sudo livecd-creator --config=discovery_fedora.ks --fslabel=Discovery --cache=/var/cache/live 
sudo rm -rf tftpboot
sudo livecd-iso-to-pxeboot Discovery.iso
