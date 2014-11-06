#!/bin/bash
interfaces() {
/sbin/ip a| awk /'^[0-9]*\:/ {print $2}' | sed 's/\:// '| sort | egrep -v "@|lo"
}

interface_info() {
        mac=`ifconfig $1 | grep ether | awk '{print $2}'`
        link_speed=`ethtool $1 2>/dev/null | egrep "Speed" | awk '{print $2}'`
        link_detected=`ethtool $1 2> /dev/null| egrep "Link det"| awk '{print $3}'`
        driver=`ethtool -i $1 | grep driver | cut -d ' ' -f 2`
	ip=`ip addr show $1 | grep inet | grep -v inet6 | awk '{print $2}'`


	if [ "${link_speed}" == "" ]; then
		link_speed='n/a'
	fi

	if [ "${link_detected}" == "" ]; then
		link_detected='n/a'
	fi

	if [ "${driver}" == "" ]; then
		driver='n/a'
	fi
        
	if [ "${ip}" == "" ]; then
		ip='none'
	fi
	echo "$1 $mac $link_speed $link_detected $driver $ip"

}

dispaly_interface_info() {
	for item in `interfaces`;do
		interface_info $item
	done
}
for item in `interfaces`;do
	interface_info $item
done
