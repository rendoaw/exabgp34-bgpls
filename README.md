[![License](https://img.shields.io/pypi/l/exabgp.svg)](https://github.com/Exa-Networks/exabgp/blob/master/COPYRIGHT)

## Overview

Basically this repo contains ExaBGP 3.4 from http://github.com/Exa-Networks/exabgp 3.4 branch with some experimental modification of :

* MP_REACH_NLRI
    * adding decoder for AFI 16388 and SAFI 71
* Adding decoder for Path Attribute TLV 29: Link State 

Current status: work in progress. 


## Example

#### How to run

```
$ sbin/exabgp exabgp.conf
```


#### ExaBGP config (as in exabgp.conf)

The following example assumes that exabgp is running on 192.168.1.154 and it has BGP-LS peering with 192.168.1.29

```
group peer {
    hold-time 180;
    local-as 64900;
    peer-as 64900;
    router-id 192.168.1.154;
    graceful-restart 1200;
    process dump_to_file {
      run ./etc/exabgp/processes/syslog-1.py;
      encoder json;
      receive {
        parsed;
        update;
        neighbor-changes;
      }
    }
    neighbor 192.168.1.29 {
        local-address 192.168.1.154;
    }
}
```


#### Router Config

Either of the following example should work. Just make sure the peering router is using TLV 29 for Link State Path Attributes.

* JunOS 

    ```
    rw@junos# show policy-options policy-statement TE
    from family traffic-engineering;
    then accept;

    [edit]
    rw@junos# show protocols mpls traffic-engineering
    database {
        import {
            policy TE;
        }
    }

    [edit]
    rw@junos# show protocols bgp
    group LS {
        type internal;
        family traffic-engineering {
            unicast;
        }
        export TE;
        neighbor 192.168.1.154;
    }
    ```

* Cisco IOS-XR Version

    ```
    router ospf 1
    distribute bgp-ls
    area 0
    network point-to-point
    mpls traffic-eng
    interface Loopback0
    !
    interface GigabitEthernet0/0/0/2.1016
    !
    interface GigabitEthernet0/0/0/2.1416
    !
    !
    mpls traffic-eng router-id Loopback0
    !
    router bgp 64900
    address-family link-state link-state
    !
    neighbor 192.168.1.154
    remote-as 64900
    local address 192.168.1.29
    session-open-mode both
    address-family link-state link-state
    !
    !
    !
    ```



#### Sample Output

* Sample Link Data

    ```
    Sun, 10 Jul 2016 01:24:08 | INFO     | 33908  | routes        | peer 192.168.1.29 ASN 64900   << UPDATE (26) (330)  attributes origin igp local-preference 100 attribute [ 0x1D 0x80 LinkState:  admin_group 00000000 available_bw{ [0] 1000000000 [1] 1000000000 [2] 1000000000 [3] 1000000000 [4] 1000000000 [5] 1000000000 [6] 1000000000 [7] 1000000000 } ipv4_router_id 10.255.0.14 max_link_bw 1000000000 max_resv_bw 1000000000 metric 1 te_metric 1 ]
    Sun, 10 Jul 2016 01:24:08 | INFO     | 33908  | routes        | peer 192.168.1.29 ASN 64900   << UPDATE (26) nlri  (184) linkstate action update local_node_id 10.255.0.14 local_asn 64900 remote_node_id 10.255.0.13 remote_asn 64900 local_ipv4 10.13.14.2 remote_ipv4 10.13.14.1 nexthop next-hop 192.168.1.29
    ```


* Sample Node Data

    ```
    Sun, 10 Jul 2016 01:24:08 | INFO     | 33908  | routes        | peer 192.168.1.29 ASN 64900   << UPDATE (27) (79)  attributes origin igp local-preference 100 attribute [ 0x1D 0x80 LinkState:  ]
    Sun, 10 Jul 2016 01:24:08 | INFO     | 33908  | routes        | peer 192.168.1.29 ASN 64900   << UPDATE (27) nlri  (148) linkstate action update local_node_id 10.255.0.16 local_asn 64900 remote_node_id  remote_asn  local_ipv4  remote_ipv4  nexthop next-hop 192.168.1.29
    ```




## To Do

* IS-IS example
* better error handling
* sample config for latest exabgp version
* clean up 
* ...


