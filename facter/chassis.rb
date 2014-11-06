#!/usr/bin/ruby
#
# facter chassis_* - get details of the parent chassis
# 

require 'facter'
require 'pp'

osfamily = Facter.value('osfamily')
devtype = Facter.value('type')
devmake = Facter.value('manufacturer')

def hp_blade()
    dev_locator = `dmidecode --type 204`.split(/\n/)
    dev_locator = dev_locator.map { |x| x.gsub(/^\s+/, '') }
    dev_locator = dev_locator.map { |x| x.gsub(/\s+$/, '') }
    dev_locator = dev_locator.map { |x| x.split(': ') }

    location = Hash.new()
    dev_locator.each {|x|
        location[x[0]] = x[1]
    }

    chassis_name = location.has_key?("Enclosure Name") ? location["Enclosure Name"] : nil
    chassis_model = location.has_key?("Enclosure Model") ? location["Enclosure Model"] : nil
    chassis_serial = location.has_key?("Enclosure Serial") ? location["Enclosure Serial"] : nil
    chassis_slot = location.has_key?("Server Bay") ? location["Server Bay"] : nil

    if chassis_slot != nil
        Facter.add("chassis") do
            setcode{ "#{chassis_name} (#{chassis_serial}) slot #{chassis_slot}" }
        end
        Facter.add("chassis_name") do
            setcode{ chassis_name }
        end
        Facter.add("chassis_model") do
            setcode{ chassis_model }
        end
        Facter.add("chassis_serial") do
            setcode{ chassis_serial }
        end
        Facter.add("chassis_slot") do
            setcode{ chassis_slot }
        end
    end
end

if osfamily == "RedHat"
    is_bmc = false
    #Look for IPMI Device
    if (devtype == 'Blade' or devtype == 'Rack Mount Chassis') and devmake == 'HP'
        hp_blade()
    end
end
