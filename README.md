# Consul_Multi_Node_Cluster
Consul Multi Node Service Mesh using Macbook, Raspberry Pi and Windows Laptop

I wanted to setup a Consul cluster to understand Service Mesh and KV store. Since we are stuck @ home, ended up bringing up a Consul cluster with nodes scatterred in my home LAN/WLAN.

Windows PC --> Consul Server </br>
MBP --> Consul Client 1. Hosting DownStream Service</br> 
Raspberry Pi --> Consul Client 2. Hosting UpStream Service</br> 

Sidecar Proxy : Consul built-in </br> 
Consul Version: Consul v1.9.0 </br> 

![topology](topology.png)

# IP Topology

Windows PC --> 192.168.128.19 </br>
MBP --> 192.168.128.9 </br> 
Raspberry Pi --> 192.168.128.28 </br> 

Credits : Thanks to [Consul tutorials](https://learn.hashicorp.com/consul) and to many people who posted articles on Consul bringup. :+1:

# Steps

## Windows

#### Start up Consul Server
> consul agent -dev -server -ui -bootstrap-expect 1 -bind 192.168.128.19 -node asgard -data-dir= path -config-dir= path </br> 
  
config-dir was empty and gave a tmp path for data-dir. In data-dir consul will store its own data <br>

## MBP

#### Start up Consul Client

> consul agent  -node=c3 -bind=192.168.128.9 -data-dir= path -config-dir= path </br> 
  
Config-dir loaded with a SVC definition with Sidecar Proxy configuration. </br> 
File_Name:dboard.json </br> 

#### Join to Cluster

> consul join 192.168.128.19

#### Downstream Service

Just used CURL to pull and use data from Upstream Service running on Pi </br> 

> curl http://localhost:9001  

#### Attach Sidecar Proxy

> consul connect proxy -sidecar-for dashboard

## Raspberry Pi

#### Start up Consul Client

> consul agent  -node=c2 -bind=192.168.128.28 -data-dir= path -config-dir= path </br> 
  
Config-dir loaded with a SVC definition with Sidecar Proxy configuration. </br> 
File_Name:time_svc_web.json </br> 

#### Join to Cluster

> consul join 192.168.128.19

#### UpStream Service

A tiny python Flask app was written to return time. </br> 
File_Name:tell_me_time.py </br> 

#### Attach Sidecar Proxy

>  consul connect proxy -sidecar-for time_web

#### Enable intention to connect both service

> consul intention create dashboard time_web

## Access Service hosted on Raspi from MBP through Service Mesh

> $>curl http://localhost:9001 </br> 
  time is 1607635269.896242

![svc](svc.png)


## Consul KV Store

Once cluster is up, we can access KV store using get/put from any node  </br> 

> c$>onsul kv put employee/employee1/name Jane </br> 
Success! Data written to: employee/employee1/name </br> 

> $>consul kv get employee/employee1/name </br> 
Jane </br> 

# Debugs

Consul runs DNS in port 8600 and UI in port 8500 </br> 

#### Web UI

![final](final.png)

#### consul members

> $> consul members </br>
Node    Address              Status  Type    Build  Protocol  DC   Segment </br>
asgard  192.168.128.19:8301  alive   server  1.9.0  2         dc1  <all> </br> 
c1      192.168.128.9:8301   alive   client  1.9.0  2         dc1  <default> </br> 
c2      192.168.128.28:8301  alive   client  1.9.0  2         dc1  <default> </br> 

#### List registered Services

> $> consul catalog services </br> 
consul </br> 
dashboard </br> 
dashboard-sidecar-proxy </br> 
time_web </br> 
time_web-sidecar-proxy </br> 


#### Use Dig to find Services 

> $> dig @127.0.0.1 -p 8600  web.service.consul </br> 

; <<>> DiG 9.10.6 <<>> @127.0.0.1 -p 8600 web.service.consul </br> 
; (1 server found) </br> 
;; global options: +cmd </br> 
;; Got answer:</br> 
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 34616</br> 
;; flags: qr aa rd; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1</br> 
;; WARNING: recursion requested but not available</br> 

;; OPT PSEUDOSECTION:</br> 
; EDNS: version: 0, flags:; udp: 4096</br> 
;; QUESTION SECTION:</br> 
;web.service.consul.		IN	A</br> 

;; AUTHORITY SECTION:</br> 
consul.			0	IN	SOA	ns.consul. hostmaster.consul. 1607736748 3600 600 86400 0</br> 

;; Query time: 7 msec</br> 
;; SERVER: 127.0.0.1#8600(127.0.0.1)</br> 
;; WHEN: Fri Dec 11 17:32:28 PST 2020</br> 
;; MSG SIZE  rcvd: 97</br> 


#### Ping to Check Services 

DNS won't resolve until we enable [DNS forwarding] (https://learn.hashicorp.com/tutorials/consul/dns-forwarding)

> $>ping time_web.service.consul  </br> 
PING time_web.service.consul (192.168.128.28): 56 data bytes  </br>
64 bytes from 192.168.128.28: icmp_seq=0 ttl=64 time=6.138 m</br>
--- time_web.service.consul ping statistics ---   </br> 
2 packets transmitted, 1 packets received, 50.0% packet loss </br> 
round-trip min/avg/max/stddev = 6.138/6.138/6.138/0.000 ms </br> 

#### Leave Consul Cluster Gracefully

> $>consul leave</br> 
Graceful leave complete </br> 
