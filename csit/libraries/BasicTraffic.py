
##############################################################
#Loading HLTAPI for Python
##############################################################
from __future__ import print_function
import sth
import time
import json
import os
import sys
import yaml
import re
from pprint import pprint
from netmiko import Netmiko


# file_path =  os.path.pardir()
# print file_path
# file_path =  os.path.dirname(os.path.basename(__file__))
file_path = os.path.dirname(os.path.realpath(__file__))

def spirent_items():
    data = yaml.load(open('/var/lib/jenkins/workspace/IQNet-L2/csit/libraries/Spirent_Test_Topology.yaml'), Loader=yaml.Loader)

    # with open( file_path + '\..\libraries\Spirent_Test_Topology.yaml') as data_file:
    #     data = yaml.load(data_file,Loader=yaml.FullLoader)
    interface_config = data['sth_interface_config']
    Booked_ports = data['Spirent_Port_Booking']
    Stream_config = data['Spirent_stream_config']
    Spirent_Test_Infra = data['Spirent_Test_Infrastructure']
    return (Booked_ports, interface_config, Stream_config, Spirent_Test_Infra)


def spi2():
    Booked_ports, Interface_config, Stream_config, Spirent_Test_Infra = spirent_items()
    test_sta = sth.test_config (
            log                                              = '1',
            logfile                                          = 'SteamConfig-WithPercentageTraffic_logfile',
            vendorlogfile                                    = 'SteamConfig-WithPercentageTraffic_stcExport',
            vendorlog                                        = '1',
            hltlog                                           = '1',
            hltlogfile                                       = 'SteamConfig-WithPercentageTraffic_hltExport',
            hlt2stcmappingfile                               = 'SteamConfig-WithPercentageTraffic_hlt2StcMapping',
            hlt2stcmapping                                   = '1',
            log_level                                        = '7');
    Number_of_ports = Spirent_Test_Infra['Number_of_ports']
    status = test_sta['status']
    if (status == '0') :
        print("run sth.test_config failed")
        print(test_sta)
    ##############################################################
    #config the parameters for optimization and parsing
    ##############################################################

    test_ctrl_sta = sth.test_control (
            action                                           = 'enable');

    status = test_ctrl_sta['status']
    if (status == '0') :
        print("run sth.test_control failed")
        print(test_ctrl_sta)
    ##############################################################
    #connect to chassis and reserve port list
    ##############################################################
    i = 0
    device = "10.91.113.124"
    port_list = list(Booked_ports.values())
    port_handle = []
    intStatus = sth.connect (
            device                                           = device,
            port_list                                        = port_list,
            break_locks                                      = 1,
            offline                                          = 0 )

    status = intStatus['status']

    if (status == '1') :
        for port in port_list :
            port_handle.append(intStatus['port_handle'][device][port])
            i += 1
    else :
        print("\nFailed to retrieve port handle!\n")
        print(port_handle)

    ##############################################################
    #interface config
    ##############################################################

    Interface_config['port_handle'] = port_handle[0]
    int_ret0 = sth.interface_config (**Interface_config)
    status = int_ret0['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret0)
    Interface_config['port_handle'] = port_handle[1]
    int_ret1 = sth.interface_config (**Interface_config)
    status = int_ret1['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret0)
    ##############################################################
    #stream config
    ##############################################################
    Stream_config['port_handle'] = port_handle[0]
    Stream_config['dest_port_list'] = port_handle[1]
    Stream_config['name'] =  'Stream From 9-3 to 9-4'
    streamblock_ret1 = sth.traffic_config(**Stream_config)
    status = streamblock_ret1['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret1)
    Stream_config['port_handle'] = port_handle[1]
    Stream_config['dest_port_list'] = port_handle[0]
    Stream_config['name'] =  'Stream From 9-4 to 9-3'
    streamblock_ret1 = sth.traffic_config(**Stream_config)
    status = streamblock_ret1['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret1)
    #############################################################
    #start traffic
    ##############################################################
    print("Traffic Started")
    traffic_ctrl_ret = sth.traffic_control (
            port_handle                                      = [port_handle[0],port_handle[1]],
            action                                           = 'run',
            duration                                         = '30');

    status = traffic_ctrl_ret['status']
    if (status == '0') :
        print("run sth.traffic_control failed")
        print(traffic_ctrl_ret)
    print("Test Traffic Stopped now adding delay before collecting stats")
    time.sleep(10)
    print("Traffic collection started")
    ##############################################################
    #start to get the traffic results
    ##############################################################
    traffic_results_ret = sth.traffic_stats (
            port_handle                                      = [port_handle[0],port_handle[1]],
            mode                                             = 'all');

    status = traffic_results_ret['status']
    if (status == '0') :
        print("run sth.traffic_stats failed")
        print(traffic_results_ret)


    result = SpirentResult(traffic_results_ret, port_list)
    return result


## Noraml L2 Traffic Load=100 Mbps, Fixed Frame=1500, Untagged
def L2_100M_F1500_Traffic():

    ##############################################################
    #config the parameters for the logging
    ##############################################################

    test_sta = sth.test_config (
            log                                              = '1',
            logfile                                          = 'L2Service_logfile',
            vendorlogfile                                    = 'L2Service_stcExport',
            vendorlog                                        = '1',
            hltlog                                           = '1',
            hltlogfile                                       = 'L2Service_hltExport',
            hlt2stcmappingfile                               = 'L2Service_hlt2StcMapping',
            hlt2stcmapping                                   = '1',
            log_level                                        = '7');

    status = test_sta['status']
    if (status == '0') :
        print("run sth.test_config failed")
        print(test_sta)
    else:
        print("***** run sth.test_config successfully")


    ##############################################################
    #config the parameters for optimization and parsing
    ##############################################################

    test_ctrl_sta = sth.test_control (
            action                                           = 'enable');

    status = test_ctrl_sta['status']
    if (status == '0') :
        print("run sth.test_control failed")
        print(test_ctrl_sta)
    else:
        print("***** run sth.test_control successfully")


    ##############################################################
    #connect to chassis and reserve port list
    ##############################################################

    i = 0
    device = "10.91.113.124"
    port_list = ['11/10','11/6']
    port_handle = []
    intStatus = sth.connect (
            device                                           = device,
            port_list                                        = port_list,
            break_locks                                      = 1,
            offline                                          = 0 )

    status = intStatus['status']

    if (status == '1') :
        for port in port_list :
            port_handle.append(intStatus['port_handle'][device][port])
            print("\n reserved ports",port,":", port_handle[i])
            i += 1
    else :
        print("\nFailed to retrieve port handle!\n")
        print(port_handle)


    ##############################################################
    #interface config
    ##############################################################

    int_ret0 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[0],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret0['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret0)
    else:
        print("***** run sth.interface_config successfully")

    int_ret1 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[1],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret1['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret1)
    else:
        print("***** run sth.interface_config successfully")


    ##############################################################
    #create device and config the protocol on it
    ##############################################################

    #start to create the device: Device 1
    device_ret0 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii',
            port_handle                                      = port_handle[1],
            router_id                                        = '192.0.0.1',
            count                                            = '1',
            enable_ping_response                             = '1',
            mac_addr                                         = '00:10:94:00:00:01',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '192.168.71.1',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '192.168.71.2',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret0['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret0)
    else:
        print("***** run sth.emulation_device_config successfully")

    #start to create the device: Device 2
    device_ret1 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii',
            port_handle                                      = port_handle[0],
            router_id                                        = '192.0.0.2',
            count                                            = '1',
            enable_ping_response                             = '1',
            mac_addr                                         = '00:10:94:00:00:02',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '192.168.71.2',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '192.168.71.1',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret1['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret1)
    else:
        print("***** run sth.emulation_device_config successfully")


    ##############################################################
    #create traffic
    ##############################################################

    src_hdl = device_ret1['handle'].split()[0]

    dst_hdl = device_ret0['handle'].split()[0]


    streamblock_ret1 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[0],
            emulation_src_handle                             = src_hdl,
            emulation_dst_handle                             = dst_hdl,
            l3_protocol                                      = 'ipv4',
            ip_id                                            = '0',
            ip_ttl                                           = '255',
            ip_hdr_length                                    = '5',
            ip_protocol                                      = '253',
            ip_fragment_offset                               = '0',
            ip_mbz                                           = '0',
            ip_precedence                                    = '6',
            ip_tos_field                                     = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '1500',
            name                                             = 'StreamBlock_1-3',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '1500',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            dest_port_list                                   = ['port1','port2'],
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_mbps                                        = '100',
            mac_discovery_gw                                 = '192.168.71.1');

    status = streamblock_ret1['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret1)
    else:
        print("***** run sth.traffic_config successfully")

    src_hdl = device_ret0['handle'].split()[0]

    dst_hdl = device_ret1['handle'].split()[0]


    streamblock_ret2 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[1],
            emulation_src_handle                             = src_hdl,
            emulation_dst_handle                             = dst_hdl,
            l3_protocol                                      = 'ipv4',
            ip_id                                            = '0',
            ip_ttl                                           = '255',
            ip_hdr_length                                    = '5',
            ip_protocol                                      = '253',
            ip_fragment_offset                               = '0',
            ip_mbz                                           = '0',
            ip_precedence                                    = '6',
            ip_tos_field                                     = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '1500',
            name                                             = 'StreamBlock_1-4',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '1500',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            dest_port_list                                   = ['port1','port2'],
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_mbps                                        = '100',
            mac_discovery_gw                                 = '192.168.71.2');

    status = streamblock_ret2['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret2)
    else:
        print("***** run sth.traffic_config successfully")

    #config part is finished

    ##############################################################
    #start devices
    ##############################################################



    ##############################################################
    #start traffic
    ##############################################################

    traffic_ctrl_ret = sth.traffic_control (
            port_handle                                      = [port_handle[0],port_handle[1]],
            action                                           = 'run',
            duration                                         = '30');

    status = traffic_ctrl_ret['status']
    if (status == '0') :
        print("run sth.traffic_control failed")
        print(traffic_ctrl_ret)
    else:
        print("***** run sth.traffic_control successfully")


    ##############################################################
    #start to get the device results
    ##############################################################
    time.sleep(30)

    ##############################################################
    #start to get the traffic results
    ##############################################################

    traffic_results_ret = sth.traffic_stats (
            port_handle                                      = [port_handle[0],port_handle[1]],
            mode                                             = 'all');

    status = traffic_results_ret['status']
    if (status == '0') :
        print("run sth.traffic_stats failed")
        print(traffic_results_ret)
    else:
        print("***** run sth.traffic_stats successfully, and results is:")
        print(traffic_results_ret)


    ##############################################################
    #clean up the session, release the ports reserved and cleanup the dbfile
    ##############################################################

    cleanup_sta = sth.cleanup_session (
            port_handle                                      = [port_handle[0],port_handle[1]],
            clean_dbfile                                     = '1');

    status = cleanup_sta['status']
    if (status == '0') :
        print("run sth.cleanup_session failed")
        print(cleanup_sta)
    else:
        print("***** run sth.cleanup_session successfully")


    print("**************Finish***************")

    result = SpirentResult(traffic_results_ret, port_list)
    return result

## Noraml L2 Traffic Load=100 Mbps, Fixed Frame=1500, Untagged
def L2_1G_F1500Traffic():

    ##############################################################
    #config the parameters for the logging
    ##############################################################

    test_sta = sth.test_config (
            log                                              = '1',
            logfile                                          = 'L2Service_logfile',
            vendorlogfile                                    = 'L2Service_stcExport',
            vendorlog                                        = '1',
            hltlog                                           = '1',
            hltlogfile                                       = 'L2Service_hltExport',
            hlt2stcmappingfile                               = 'L2Service_hlt2StcMapping',
            hlt2stcmapping                                   = '1',
            log_level                                        = '7');

    status = test_sta['status']
    if (status == '0') :
        print("run sth.test_config failed")
        print(test_sta)
    else:
        print("***** run sth.test_config successfully")


    ##############################################################
    #config the parameters for optimization and parsing
    ##############################################################

    test_ctrl_sta = sth.test_control (
            action                                           = 'enable');

    status = test_ctrl_sta['status']
    if (status == '0') :
        print("run sth.test_control failed")
        print(test_ctrl_sta)
    else:
        print("***** run sth.test_control successfully")


    ##############################################################
    #connect to chassis and reserve port list
    ##############################################################

    i = 0
    device = "10.91.113.124"
    port_list = ['11/10','11/6']
    port_handle = []
    intStatus = sth.connect (
            device                                           = device,
            port_list                                        = port_list,
            break_locks                                      = 1,
            offline                                          = 0 )

    status = intStatus['status']

    if (status == '1') :
        for port in port_list :
            port_handle.append(intStatus['port_handle'][device][port])
            print("\n reserved ports",port,":", port_handle[i])
            i += 1
    else :
        print("\nFailed to retrieve port handle!\n")
        print(port_handle)


    ##############################################################
    #interface config
    ##############################################################

    int_ret0 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[0],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret0['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret0)
    else:
        print("***** run sth.interface_config successfully")

    int_ret1 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[1],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret1['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret1)
    else:
        print("***** run sth.interface_config successfully")


    ##############################################################
    #create device and config the protocol on it
    ##############################################################

    #start to create the device: Device 1
    device_ret0 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii',
            port_handle                                      = port_handle[1],
            router_id                                        = '192.0.0.1',
            count                                            = '1',
            enable_ping_response                             = '1',
            mac_addr                                         = '00:10:94:00:00:01',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '192.168.71.1',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '192.168.71.2',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret0['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret0)
    else:
        print("***** run sth.emulation_device_config successfully")

    #start to create the device: Device 2
    device_ret1 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii',
            port_handle                                      = port_handle[0],
            router_id                                        = '192.0.0.2',
            count                                            = '1',
            enable_ping_response                             = '1',
            mac_addr                                         = '00:10:94:00:00:02',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '192.168.71.2',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '192.168.71.1',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret1['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret1)
    else:
        print("***** run sth.emulation_device_config successfully")


    ##############################################################
    #create traffic
    ##############################################################

    src_hdl = device_ret1['handle'].split()[0]

    dst_hdl = device_ret0['handle'].split()[0]


    streamblock_ret1 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[0],
            emulation_src_handle                             = src_hdl,
            emulation_dst_handle                             = dst_hdl,
            l3_protocol                                      = 'ipv4',
            ip_id                                            = '0',
            ip_ttl                                           = '255',
            ip_hdr_length                                    = '5',
            ip_protocol                                      = '253',
            ip_fragment_offset                               = '0',
            ip_mbz                                           = '0',
            ip_precedence                                    = '6',
            ip_tos_field                                     = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '1500',
            name                                             = 'StreamBlock_1-3',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '1500',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            dest_port_list                                   = ['port1','port2'],
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_mbps                                        = '1000',
            mac_discovery_gw                                 = '192.168.71.1');

    status = streamblock_ret1['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret1)
    else:
        print("***** run sth.traffic_config successfully")

    src_hdl = device_ret0['handle'].split()[0]

    dst_hdl = device_ret1['handle'].split()[0]


    streamblock_ret2 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[1],
            emulation_src_handle                             = src_hdl,
            emulation_dst_handle                             = dst_hdl,
            l3_protocol                                      = 'ipv4',
            ip_id                                            = '0',
            ip_ttl                                           = '255',
            ip_hdr_length                                    = '5',
            ip_protocol                                      = '253',
            ip_fragment_offset                               = '0',
            ip_mbz                                           = '0',
            ip_precedence                                    = '6',
            ip_tos_field                                     = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '1500',
            name                                             = 'StreamBlock_1-4',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '1500',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            dest_port_list                                   = ['port1','port2'],
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_mbps                                        = '1000',
            mac_discovery_gw                                 = '192.168.71.2');

    status = streamblock_ret2['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret2)
    else:
        print("***** run sth.traffic_config successfully")

    #config part is finished

    ##############################################################
    #start devices
    ##############################################################



    ##############################################################
    #start traffic
    ##############################################################

    traffic_ctrl_ret = sth.traffic_control (
            port_handle                                      = [port_handle[0],port_handle[1]],
            action                                           = 'run',
            duration                                         = '30');

    status = traffic_ctrl_ret['status']
    if (status == '0') :
        print("run sth.traffic_control failed")
        print(traffic_ctrl_ret)
    else:
        print("***** run sth.traffic_control successfully")


    ##############################################################
    #start to get the device results
    ##############################################################
    time.sleep(30)

    ##############################################################
    #start to get the traffic results
    ##############################################################

    traffic_results_ret = sth.traffic_stats (
            port_handle                                      = [port_handle[0],port_handle[1]],
            mode                                             = 'all');

    status = traffic_results_ret['status']
    if (status == '0') :
        print("run sth.traffic_stats failed")
        print(traffic_results_ret)
    else:
        print("***** run sth.traffic_stats successfully, and results is:")
        print(traffic_results_ret)


    ##############################################################
    #clean up the session, release the ports reserved and cleanup the dbfile
    ##############################################################

    cleanup_sta = sth.cleanup_session (
            port_handle                                      = [port_handle[0],port_handle[1]],
            clean_dbfile                                     = '1');

    status = cleanup_sta['status']
    if (status == '0') :
        print("run sth.cleanup_session failed")
        print(cleanup_sta)
    else:
        print("***** run sth.cleanup_session successfully")


    print("**************Finish***************")

    result = SpirentResult(traffic_results_ret, port_list)
    return result



## TI-LFA FAILURE
def FAILURE_TILFA():

    ##############################################################
    #config the parameters for the logging
    ##############################################################

    test_sta = sth.test_config (
            log                                              = '0',
            logfile                                          = 'failure_logfile',
            vendorlogfile                                    = 'failure_stcExport',
            vendorlog                                        = '0',
            hltlog                                           = '1',
            hltlogfile                                       = 'failure_hltExport',
            hlt2stcmappingfile                               = 'failure_hlt2StcMapping',
            hlt2stcmapping                                   = '1',
            log_level                                        = '0');

    status = test_sta['status']
    if (status == '0') :
        print("run sth.test_config failed")
        print(test_sta)
    else:
        print("***** run sth.test_config successfully")


    ##############################################################
    #config the parameters for optimization and parsing
    ##############################################################

    test_ctrl_sta = sth.test_control (
            action                                           = 'enable');

    status = test_ctrl_sta['status']
    if (status == '0') :
        print("run sth.test_control failed")
        print(test_ctrl_sta)
    else:
        print("***** run sth.test_control successfully")


    ##############################################################
    #connect to chassis and reserve port list
    ##############################################################

    i = 0
    device = "10.91.113.124"
    port_list = ['11/6','11/10']
    port_handle = []
    intStatus = sth.connect (
            device                                           = device,
            port_list                                        = port_list,
            break_locks                                      = 1,
            offline                                          = 0,
            reset                                            = 1)

    status = intStatus['status']

    if (status == '1') :
        for port in port_list :
            port_handle.append(intStatus['port_handle'][device][port])
            print("\n reserved ports",port,":", port_handle[i])
            i += 1
    else :
        print("\nFailed to retrieve port handle!\n")
        print(port_handle)


    ##############################################################
    #interface config
    ##############################################################

    int_ret0 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[0],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret0['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret0)
    else:
        print("***** run sth.interface_config successfully")

    int_ret1 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[1],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret1['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret1)
    else:
        print("***** run sth.interface_config successfully")


    ##############################################################
    #create device and config the protocol on it
    ##############################################################

    #start to create the device: Device 1
    device_ret0 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii_vlan',
            port_handle                                      = port_handle[0],
            vlan_user_pri                                    = '0',
            vlan_cfi                                         = '0',
            vlan_id                                          = '50',
            vlan_tpid                                        = '33024',
            vlan_id_repeat_count                             = '0',
            vlan_id_step                                     = '0',
            router_id                                        = '192.0.0.1',
            count                                            = '1',
            enable_ping_response                             = '0',
            mac_addr                                         = '00:10:94:13:00:01',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '10.50.0.13',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '10.50.0.14',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret0['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret0)
    else:
        print("***** run sth.emulation_device_config successfully")

    #start to create the device: Device 2
    device_ret1 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii_vlan',
            port_handle                                      = port_handle[1],
            vlan_user_pri                                    = '0',
            vlan_cfi                                         = '0',
            vlan_id                                          = '50',
            vlan_tpid                                        = '33024',
            vlan_id_repeat_count                             = '0',
            vlan_id_step                                     = '0',
            router_id                                        = '192.0.0.2',
            count                                            = '1',
            enable_ping_response                             = '0',
            mac_addr                                         = '00:10:94:14:00:01',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '10.50.0.14',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '10.50.0.13',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret1['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret1)
    else:
        print("***** run sth.emulation_device_config successfully")


    ##############################################################
    #create traffic
    ##############################################################

    streamblock_ret1 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[0],
            l2_encap                                         = 'ethernet_ii_vlan',
            vlan_id_repeat                                   = '0',
            vlan_id_mode                                     = 'increment',
            vlan_id_count                                    = '1',
            vlan_id_step                                     = '1',
            mac_src                                          = '00:10:94:13:00:01',
            mac_dst                                          = '00:10:94:14:00:01',
            vlan_cfi                                         = '0',
            vlan_tpid                                        = '33024',
            vlan_id                                          = '49',
            vlan_user_priority                               = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '9078',
            name                                             = 'StreamBlock_2',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '9100',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_pps                                        = '1000',
            enable_stream                                    = 'false');

    status = streamblock_ret1['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret1)
    else:
        print("***** run sth.traffic_config successfully")

    streamblock_ret2 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[1],
            l2_encap                                         = 'ethernet_ii_vlan',
            vlan_id_repeat                                   = '0',
            vlan_id_mode                                     = 'increment',
            vlan_id_count                                    = '1',
            vlan_id_step                                     = '1',
            mac_src                                          = '00:10:94:14:00:01',
            mac_dst                                          = '00:10:94:13:00:01',
            vlan_cfi                                         = '0',
            vlan_tpid                                        = '33024',
            vlan_id                                          = '49',
            vlan_user_priority                               = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '9078',
            name                                             = 'StreamBlock_5',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '9100',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_pps                                        = '1000',
            enable_stream                                    = 'false');

    status = streamblock_ret2['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret2)
    else:
        print("***** run sth.traffic_config successfully")

    #config part is finished

    ##############################################################
    #start devices
    ##############################################################
    print("***** sending 30 sec initial traffic for mac-learning")
    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='run',
        duration='30');
    time.sleep(5)
    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='stop')
    print("***** mac learning done")
    print("***** clear the stats stats of the Traffic")
    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='clear_stats');
    time.sleep(10)

    ##############################################################
    #start traffic
    ##############################################################


    traffic_ctrl_ret = sth.traffic_control (
            port_handle                                      = [port_handle[0],port_handle[1]],
            action                                           = 'run',
            duration                                         = '120');

    status = traffic_ctrl_ret['status']
    if (status == '0') :
        print("run sth.traffic_control failed")
        print(traffic_ctrl_ret)
    else:
        print("***** run sth.traffic_control successfully")

    print("***** Wait for traffic to stop")
    time.sleep(30)
    print("***** 30 seconds sleep done")
    print("***** log in to device")


    ## Login to device and shut the port
    cisco1 = {
        "host": "10.91.126.199",
        "username": "dshaw1",
        "password": "N0@ught33b0y",
        "device_type": "cisco_xr",
    }

    net_connect = Netmiko(**cisco1)
    command = ['int HundredGigE0/0/1/0','shut']

    print()
    print(net_connect.find_prompt())
    output = net_connect.send_config_set(command)
    net_connect.commit()
    net_connect.exit_config_mode()
    #output += net_connect.send_command("show int HundredGigE0/0/1/0")
    net_connect.disconnect()
    print(output)
    print()

    print("***** log out of device")
    time.sleep(90)
    print("***** 90 seconds sleep done")

    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='stop')
    print("***** traffic stopped")

    ##############################################################
    #start to get the device results
    ##############################################################


    ##############################################################
    #start to get the traffic results
    ##############################################################

    traffic_results_ret = sth.traffic_stats (
            port_handle                                      = [port_handle[0],port_handle[1]],
            mode                                             = 'all');

    status = traffic_results_ret['status']
    if (status == '0') :
        print("run sth.traffic_stats failed")
        # print(traffic_results_ret)
    else:
        print("***** run sth.traffic_stats successfully, and results is:")
        # pprint(traffic_results_ret)

    traffic_result = str(traffic_results_ret)
    DROP = '(streamblock\d+).*?\s+\S+(dropped_pkts)\S+\s+\S+(\d+)'
    RX = '(streamblock\d+).*?(rx).*?(total_pkts).*?(\d+)'
    TX = '(streamblock\d+).*?(tx).*?(total_pkts).*?(\d+)'
    pkt_drop = re.findall(DROP, traffic_result)
    rx_stats = re.findall(RX, traffic_result)
    tx_stats = re.findall(TX, traffic_result)

    if ((int(pkt_drop[0][2]) == 0) and (int(pkt_drop[1][2]) == 0)):
        status = 'pass'
    else:
        status = 'fail'

    OverallStatus = str(rx_stats) + '\n' + str(tx_stats) + '\n' +str(pkt_drop) + '\n' + status
    print(OverallStatus)
    return OverallStatus


    # port1_RX = traffic_results_ret['port1']['stream']['streamblock1']['rx']['total_pkts']
    # port1_TX = traffic_results_ret['port1']['stream']['streamblock1']['tx']['total_pkts']
    # port2_RX = traffic_results_ret['port2']['stream']['streamblock2']['rx']['total_pkts']
    # port2_TX = traffic_results_ret['port2']['stream']['streamblock2']['tx']['total_pkts']
    # drop1 = traffic_results_ret['port1']['stream']['streamblock1']['rx']['dropped_pkts']
    # drop2 = traffic_results_ret['port2']['stream']['streamblock2']['rx']['dropped_pkts']
    # if ((int(drop1) == 0) and (int(drop2) == 0)):
    #     print("****** test case has passed")
    #     print("***received traffic on Port1:                    			" + str(port1_RX))
    #     print("***sent traffic from Port1:                      			" + str(port1_TX))
    #     print("***received traffic on Port2:                    			" + str(port2_RX))
    #     print("***sent traffic from Port2:                      			" + str(port2_TX))
    #     print("***drop from Port2_AR13 to Port1_AR14:                     	" + str(drop1))
    #     print("***drop from Port1_AR14 to port2_AR13:                     	" + str(drop2))
    # else:
    #     print("***** test could not pass, there is drop in the Traffic")
    #     print("***received traffic on Port1:                    			" + str(port1_RX))
    #     print("***sent traffic on Port1::                       			" + str(port1_TX))
    #     print("***received traffic on Port2:                    			" + str(port2_RX))
    #     print("***sent traffic on Port2:                        			" + str(port2_TX))
    #     print("***drop from Port2_AR13 to Port1_AR14:                     	" + str(drop1))
    #     print("***drop from Port1_AR14 to port2_AR13:                     	" + str(drop2))
    ##############################################################
    #clean up the session, release the ports reserved and cleanup the dbfile
    ##############################################################

    cleanup_sta = sth.cleanup_session (
            port_handle                                      = [port_handle[0],port_handle[1]],
            clean_dbfile                                     = '1');

    status = cleanup_sta['status']
    if (status == '0') :
        print("run sth.cleanup_session failed")
        print(cleanup_sta)
    else:
        print("***** run sth.cleanup_session successfully")


    print("**************Finish***************")

## TI-LFA REPAIR
def REPAIR_TILFA():

    test_sta = sth.test_config (
            log                                              = '0',
            logfile                                          = 'repair_logfile',
            vendorlogfile                                    = 'repair_stcExport',
            vendorlog                                        = '0',
            hltlog                                           = '1',
            hltlogfile                                       = 'repair_hltExport',
            hlt2stcmappingfile                               = 'repair_hlt2StcMapping',
            hlt2stcmapping                                   = '1',
            log_level                                        = '0');

    status = test_sta['status']
    if (status == '0') :
        print("run sth.test_config failed")
        print(test_sta)
    else:
        print("***** run sth.test_config successfully")


    ##############################################################
    #config the parameters for optimization and parsing
    ##############################################################

    test_ctrl_sta = sth.test_control (
            action                                           = 'enable');

    status = test_ctrl_sta['status']
    if (status == '0') :
        print("run sth.test_control failed")
        print(test_ctrl_sta)
    else:
        print("***** run sth.test_control successfully")


    ##############################################################
    #connect to chassis and reserve port list
    ##############################################################

    i = 0
    device = "10.91.113.124"
    port_list = ['11/6','11/10']
    port_handle = []
    intStatus = sth.connect (
            device                                           = device,
            port_list                                        = port_list,
            break_locks                                      = 1,
            offline                                          = 0,
            reset                                            = 1)

    status = intStatus['status']

    if (status == '1') :
        for port in port_list :
            port_handle.append(intStatus['port_handle'][device][port])
            print("\n reserved ports",port,":", port_handle[i])
            i += 1
    else :
        print("\nFailed to retrieve port handle!\n")
        print(port_handle)


    ##############################################################
    #interface config
    ##############################################################

    int_ret0 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[0],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret0['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret0)
    else:
        print("***** run sth.interface_config successfully")

    int_ret1 = sth.interface_config (
            mode                                             = 'config',
            port_handle                                      = port_handle[1],
            create_host                                      = 'false',
            intf_mode                                        = 'ethernet',
            phy_mode                                         = 'fiber',
            scheduling_mode                                  = 'RATE_BASED',
            port_loadunit                                    = 'PERCENT_LINE_RATE',
            port_load                                        = '10',
            enable_ping_response                             = '0',
            control_plane_mtu                                = '1500',
            flow_control                                     = 'false',
            speed                                            = 'ether1000',
            data_path_mode                                   = 'normal',
            autonegotiation                                  = '1');

    status = int_ret1['status']
    if (status == '0') :
        print("run sth.interface_config failed")
        print(int_ret1)
    else:
        print("***** run sth.interface_config successfully")


    ##############################################################
    #create device and config the protocol on it
    ##############################################################

    #start to create the device: Device 1
    device_ret0 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii_vlan',
            port_handle                                      = port_handle[0],
            vlan_user_pri                                    = '0',
            vlan_cfi                                         = '0',
            vlan_id                                          = '50',
            vlan_tpid                                        = '33024',
            vlan_id_repeat_count                             = '0',
            vlan_id_step                                     = '0',
            router_id                                        = '192.0.0.1',
            count                                            = '1',
            enable_ping_response                             = '0',
            mac_addr                                         = '00:10:94:13:00:01',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '10.50.0.13',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '10.50.0.14',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret0['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret0)
    else:
        print("***** run sth.emulation_device_config successfully")

    #start to create the device: Device 2
    device_ret1 = sth.emulation_device_config (
            mode                                             = 'create',
            ip_version                                       = 'ipv4',
            encapsulation                                    = 'ethernet_ii_vlan',
            port_handle                                      = port_handle[1],
            vlan_user_pri                                    = '0',
            vlan_cfi                                         = '0',
            vlan_id                                          = '50',
            vlan_tpid                                        = '33024',
            vlan_id_repeat_count                             = '0',
            vlan_id_step                                     = '0',
            router_id                                        = '192.0.0.2',
            count                                            = '1',
            enable_ping_response                             = '0',
            mac_addr                                         = '00:10:94:14:00:01',
            mac_addr_step                                    = '00:00:00:00:00:01',
            intf_ip_addr                                     = '10.50.0.14',
            intf_prefix_len                                  = '24',
            resolve_gateway_mac                              = 'true',
            gateway_ip_addr                                  = '10.50.0.13',
            gateway_ip_addr_step                             = '0.0.0.0',
            intf_ip_addr_step                                = '0.0.0.1');

    status = device_ret1['status']
    if (status == '0') :
        print("run sth.emulation_device_config failed")
        print(device_ret1)
    else:
        print("***** run sth.emulation_device_config successfully")


    ##############################################################
    #create traffic
    ##############################################################

    streamblock_ret1 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[0],
            l2_encap                                         = 'ethernet_ii_vlan',
            vlan_id_repeat                                   = '0',
            vlan_id_mode                                     = 'increment',
            vlan_id_count                                    = '1',
            vlan_id_step                                     = '1',
            mac_src                                          = '00:10:94:13:00:01',
            mac_dst                                          = '00:10:94:14:00:01',
            vlan_cfi                                         = '0',
            vlan_tpid                                        = '33024',
            vlan_id                                          = '49',
            vlan_user_priority                               = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '9078',
            name                                             = 'StreamBlock_2',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '9100',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_pps                                        = '1000',
            enable_stream                                    = 'false');

    status = streamblock_ret1['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret1)
    else:
        print("***** run sth.traffic_config successfully")

    streamblock_ret2 = sth.traffic_config (
            mode                                             = 'create',
            port_handle                                      = port_handle[1],
            l2_encap                                         = 'ethernet_ii_vlan',
            vlan_id_repeat                                   = '0',
            vlan_id_mode                                     = 'increment',
            vlan_id_count                                    = '1',
            vlan_id_step                                     = '1',
            mac_src                                          = '00:10:94:14:00:01',
            mac_dst                                          = '00:10:94:13:00:01',
            vlan_cfi                                         = '0',
            vlan_tpid                                        = '33024',
            vlan_id                                          = '49',
            vlan_user_priority                               = '0',
            enable_control_plane                             = '0',
            l3_length                                        = '9078',
            name                                             = 'StreamBlock_5',
            fill_type                                        = 'constant',
            fcs_error                                        = '0',
            fill_value                                       = '0',
            frame_size                                       = '9100',
            traffic_state                                    = '1',
            high_speed_result_analysis                       = '1',
            length_mode                                      = 'fixed',
            tx_port_sending_traffic_to_self_en               = 'false',
            disable_signature                                = '0',
            enable_stream_only_gen                           = '1',
            pkts_per_burst                                   = '1',
            inter_stream_gap_unit                            = 'bytes',
            inter_stream_gap                                 = '12',
            rate_pps                                        = '1000',
            enable_stream                                    = 'false');

    status = streamblock_ret2['status']
    if (status == '0') :
        print("run sth.traffic_config failed")
        print(streamblock_ret2)
    else:
        print("***** run sth.traffic_config successfully")

    #config part is finished

    ##############################################################
    #start devices
    ##############################################################
    print("***** sending 30 sec initial traffic for mac-learning")
    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='run',
        duration='30');
    time.sleep(5)
    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='stop')
    print("***** mac learning done")
    print("***** clear the stats stats of the Traffic")
    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='clear_stats');
    time.sleep(10)

    ##############################################################
    #start traffic
    ##############################################################


    traffic_ctrl_ret = sth.traffic_control (
            port_handle                                      = [port_handle[0],port_handle[1]],
            action                                           = 'run',
            duration                                         = '120');

    status = traffic_ctrl_ret['status']
    if (status == '0') :
        print("run sth.traffic_control failed")
        print(traffic_ctrl_ret)
    else:
        print("***** run sth.traffic_control successfully")

    print("***** Wait for traffic to stop")
    time.sleep(30)
    print("***** 30 seconds sleep done")
    print("***** log in to device")
    cisco1 = {
        "host": "10.91.126.199",
        "username": "dshaw1",
        "password": "N0@ught33b0y",
        "device_type": "cisco_xr",
    }

    net_connect = Netmiko(**cisco1)
    command = ['int HundredGigE0/0/1/0','no shut']

    print()
    print(net_connect.find_prompt())
    output = net_connect.send_config_set(command)
    net_connect.commit()
    net_connect.exit_config_mode()
    #output += net_connect.send_command("show int HundredGigE0/0/1/0")
    net_connect.disconnect()
    print(output)
    print()

    print("***** log out of device")
    time.sleep(90)
    print("***** 90 seconds sleep done")

    traffic_ctrl_ret = sth.traffic_control(
        port_handle=[port_handle[0], port_handle[1]],
        action='stop')
    print("***** traffic stopped")

    ##############################################################
    #start to get the device results
    ##############################################################


    ##############################################################
    #start to get the traffic results
    ##############################################################

    traffic_results_ret = sth.traffic_stats (
            port_handle                                      = [port_handle[0],port_handle[1]],
            mode                                             = 'all');

    status = traffic_results_ret['status']
    if (status == '0') :
        print("run sth.traffic_stats failed")
        print(traffic_results_ret)
    else:
        print("***** run sth.traffic_stats successfully, and results is:")
        pprint(traffic_results_ret)

    traffic_result = str(traffic_results_ret)
    DROP = '(streamblock\d+).*?\s+\S+(dropped_pkts)\S+\s+\S+(\d+)'
    RX = '(streamblock\d+).*?(rx).*?(total_pkts).*?(\d+)'
    TX = '(streamblock\d+).*?(tx).*?(total_pkts).*?(\d+)'
    pkt_drop = re.findall(DROP, traffic_result)
    rx_stats = re.findall(RX, traffic_result)
    tx_stats = re.findall(TX, traffic_result)

    if ((int(pkt_drop[0][2]) == 0) and (int(pkt_drop[1][2]) == 0)):
        status = 'pass'
    else:
        status = 'fail'

    OverallStatus = str(rx_stats) + '\n' + str(tx_stats) + '\n' +str(pkt_drop) + '\n' + status
    print(OverallStatus)
    return OverallStatus

    # port1_RX = traffic_results_ret['port1']['stream']['streamblock1']['rx']['total_pkts']
    # port1_TX = traffic_results_ret['port1']['stream']['streamblock1']['tx']['total_pkts']
    # port2_RX = traffic_results_ret['port2']['stream']['streamblock2']['rx']['total_pkts']
    # port2_TX = traffic_results_ret['port2']['stream']['streamblock2']['tx']['total_pkts']
    # drop1 = traffic_results_ret['port1']['stream']['streamblock1']['rx']['dropped_pkts']
    # drop2 = traffic_results_ret['port2']['stream']['streamblock2']['rx']['dropped_pkts']
    # if ((int(drop1) == 0) and (int(drop2) == 0)):
    # 	print("****** test case has passed")
    # 	print("***received traffic on Port1:                    			" + str(port1_RX))
    # 	print("***sent traffic from Port1:                      			" + str(port1_TX))
    # 	print("***received traffic on Port2:                    			" + str(port2_RX))
    # 	print("***sent traffic from Port2:                      			" + str(port2_TX))
    # 	print("***drop from Port2_AR13 to Port1_AR14:                     	" + str(drop1))
    # 	print("***drop from Port1_AR14 to port2_AR13:                     	" + str(drop2))
    # else:
    # 	print("***** test could not pass, there is drop in the Traffic")
    # 	print("***received traffic on Port1:                    			" + str(port1_RX))
    # 	print("***sent traffic on Port1::                       			" + str(port1_TX))
    # 	print("***received traffic on Port2:                    			" + str(port2_RX))
    # 	print("***sent traffic on Port2:                        			" + str(port2_TX))
    # 	print("***drop from Port2_AR13 to Port1_AR14:                     	" + str(drop1))
    # 	print("***drop from Port1_AR14 to port2_AR13:                     	" + str(drop2))
    ##############################################################
    #clean up the session, release the ports reserved and cleanup the dbfile
    ##############################################################


    cleanup_sta = sth.cleanup_session (
            port_handle                                      = [port_handle[0],port_handle[1]],
            clean_dbfile                                     = '1');

    status = cleanup_sta['status']
    if (status == '0') :
        print("run sth.cleanup_session failed")
        print(cleanup_sta)
    else:
        print("***** run sth.cleanup_session successfully")


    print("**************Finish***************")



def SpirentResult(traffic_results_ret, port_list):

    ##############################################################
    #Get required values from Stats
    ##############################################################

    traffic_result = str(traffic_results_ret)

    #regex to get rx, tx and streams from traffic_results_ret
    RX = '(streamblock\d+)\S+\s+\S+(rx)\S+\s+\S+total_pkt_bytes\S+\s+\S(\d+)'
    TX = '(streamblock\d+).*?(tx)\S+\s+\S+total_pkt_bytes\S+\s+\S(\d+)'
    StreamBlock = 'streamblock\d+'


    print('Spirent Ports= ' + str(port_list) + '\nTotal Ports= ' + str(len(port_list)))
    PortStatus = 'Spirent Ports= ' + str(port_list) + '\nTotal Ports= ' + str(len(port_list))

    StreamBlock = re.findall(StreamBlock, traffic_result)
    print('Stream Configured= ' + str(StreamBlock) + '\nTotal Streams= ' + str(len(StreamBlock)))
    StreamStatus = 'Stream Configured= ' + str(StreamBlock) + '\nTotal Streams= ' + str(len(StreamBlock))

    rx_stats = re.findall(RX, traffic_result)
    tx_stats = re.findall(TX, traffic_result)

    print('rx_stats= ' + str(rx_stats))
    print('tx_stats= ' + str(tx_stats))

    stats = 'rx_stats= ' + str(rx_stats) + '\ntx_stats= ' + str(tx_stats)

    StreamResult = []

    for i in range(0,len(StreamBlock)):
        if rx_stats[i][2] == tx_stats[i][2]:
            print(str(rx_stats[i][0] + ' = pass'))
            StreamResult.append('pass')

        else:
            print(str(rx_stats[i][0] + ' = fail'))
            StreamResult.append('fail')

    print(str(StreamResult))

    OverallStatus = '\n' + PortStatus + '\n' + StreamStatus + '\n' + stats + '\n' + str(StreamResult)
    print(OverallStatus)

    return OverallStatus



