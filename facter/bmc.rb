#!/usr/bin/ruby
#
# facter bmc_* - get details of ipmi controllers
# 

require 'facter'
require 'pp'

osfamily = Facter.value('osfamily')

def get_ipmi_check()
    if File.exists?( '/scripts/check_ipmi_sensor' )
        return '/scripts/check_ipmi_sensor'
    end

    if File.exists?( '/usr/lib64/nagios/plugins/check_ipmi_sensor' )
        return '/usr/lib64/nagios/plugins/check_ipmi_sensor'
    end

    return nil
end

def bmc()
    if File.exists?( '/usr/bin/ipmitool' )
        Facter.add("bmc_tool") do
            setcode{ 'ipmitool' }
        end
        
        sensor_cmd = get_ipmi_check()

        if sensor_cmd != nil
            ipmi_sensors = `#{sensor_cmd} -H localhost`
            ipmi_sensors_status = $?.exitstatus

            Facter.add("bmc_sensors") do
                setcode{ ipmi_sensors }
            end

            Facter.add("bmc_sensors_status") do
                setcode{ ipmi_sensors_status }
            end
        end
        ipmi_raw = `/usr/bin/ipmitool lan print`.split(/\n/)
        ipmi_raw = ipmi_raw.map { |x| x.gsub(/^\s+:\s+/, '') }
        ipmi_raw = ipmi_raw.map { |x| x.gsub(/\s+:\s+/, '||') }
        ipmi_raw = ipmi_raw.map { |x| x.split('||') }

        ipmi_hash = Hash.new()
        ipmi_raw.each {|x|
            ipmi_hash[x[0]] = x[1]
        }

        ip = ipmi_hash.has_key?("IP Address") ? ipmi_hash["IP Address"] : nil
        ip_mode = ipmi_hash.has_key?("IP Address Source") ? ipmi_hash["IP Address Source"] : nil
        mask = ipmi_hash.has_key?("Subnet Mask") ? ipmi_hash["Subnet Mask"] : nil
        gateway = ipmi_hash.has_key?("Default Gateway IP") ? ipmi_hash["Default Gateway IP"] : nil
        mac = ipmi_hash.has_key?("MAC Address") ? ipmi_hash["MAC Address"] : nil

        Facter.add("bmc_ip") do
            setcode{ ip }
        end
        Facter.add("bmc_ip_mode") do
            setcode{ ip_mode }
        end
        Facter.add("bmc_mask") do
            setcode{ mask }
        end
        Facter.add("bmc_gateway") do
            setcode{ gateway }
        end
        Facter.add("bmc_mac") do
            setcode{ mac }
        end
    else
        Facter.add("bmc_tool") do
            setcode{ false }
        end
    end

    return true
end

if osfamily == "RedHat"
    is_bmc = false
    #Look for IPMI Device
    if File.exists?( '/dev/ipmi0' )
        is_bmc = true if bmc()
    end

    Facter.add( "is_bmc" ) do
        setcode{ is_bmc }
    end
end
