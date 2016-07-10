# encoding: utf-8
"""
linkstate.py

Created by rendo.aw@gmail.com
"""

from struct import unpack
from struct import pack
from exabgp.protocol.ip import IP
from exabgp.protocol.family import AFI
from exabgp.protocol.family import SAFI
from exabgp.bgp.message import OUT
from exabgp.bgp.message.notification import Notify
from exabgp.bgp.message.update.nlri.nlri import NLRI
from exabgp.bgp.message.update.nlri.qualifier.rd import RouteDistinguisher

import binascii


def _unique ():
        value = 0
        while True:
                yield value
                value += 1
        
def decode_tlv(data, offset, type_len, length_len):
        t, = unpack('!H',data[offset:offset+type_len])
        l, = unpack('!H',data[offset+type_len:offset+type_len+length_len])
        v = data[offset+type_len+length_len:offset+type_len+length_len+l]
        return (t,l,v)

unique = _unique()


class LSTLV():
        LOCAL_NODE_DESCRIPTORS          = 256
        REMOTE_NODE_DESCRIPTORS         = 257
        LOCAL_IPV4                      = 259
        REMOTE_IPV4                     = 260
        ASN                             = 512
        BGPLS_ID                        = 513
        OSPF_AREA_ID                    = 514
        IGP_ROUTER_ID                   = 515


class BGPLS(NLRI):

        __slots__ = ['action','nexthop','local_node_id','local_asn','remote_node_id','remote_asn','local_ipv4','remote_ipv4','action_str']

        def __init__ (self, local_node_id, local_asn, remote_node_id, remote_asn, local_ipv4, remote_ipv4, action):
                NLRI.__init__(self,AFI.bgpls,SAFI.bgp_ls)
                self.action = OUT.ANNOUNCE
                self.nexthop = None
                self.local_node_id = local_node_id
                self.local_asn = local_asn
                self.remote_node_id = remote_node_id
                self.remote_asn = remote_asn
                self.local_ipv4 = local_ipv4
                self.remote_ipv4 = remote_ipv4
                if action == 1:
                    self.action_str = "update"
                elif action == 2:
                    self.action_str = "withdraw"
                else:
                    self.action_str = "unknown"


        
        def index (self):
                return self.pack()

        def pack (self, addpath=None):
                return '%s%s%s%s' % (
                        '\x00\x11',  # pack('!H',17)
                        self.rd.pack(),
                        pack(
                                '!HHH',
                                self.ve,
                                self.offset,
                                self.size
                        ),
                        pack(
                                '!L',
                                (self.base << 4) | 0x1
                        )[1:]  # setting the bottom of stack, should we ?
                )

        def json (self):
                content = ', '.join([
                        '"action": "%s"' % self.action_str,
                        '"local_node_id": "%s"' % self.local_node_id,
                        '"local_asn": "%s"' % self.local_asn,
                        '"remote_node_id": "%s"' % self.remote_node_id,
                        '"remote_asn": "%s"' % self.remote_asn,
                        '"local_ipv4": "%s"' % self.local_ipv4,
                        '"remote_ipv4": "%s"' % self.remote_ipv4,
                ])
                return '"linkstate": { %s }' % content

        def extensive (self):
                return "linkstate action %s local_node_id %s local_asn %s remote_node_id %s remote_asn %s local_ipv4 %s remote_ipv4 %s nexthop %s" % (
                        self.action_str, 
                        self.local_node_id,
                        self.local_asn,
                        self.remote_node_id,
                        self.remote_asn,
                        self.local_ipv4,
                        self.remote_ipv4,
                        '' if self.nexthop is None else 'next-hop %s' % self.nexthop,
                )

        def __str__ (self):
                return self.extensive()




        @classmethod
        def unpack (cls, afi, safi, data, addpath, nexthop, action):
                local_node_id = ""
                local_asn = ""
                local_ipv4 = ""
                remote_node_id = ""
                remote_asn = ""
                remote_ipv4 = ""
                
                nlri_type = data[0:2]
                nlri_length, = unpack('!H',data[2:4])
                protocol_id = data[4:5]
                topology_type = data[5:13]
                nlri_offset = 13
                nlri_cur_pos = 0
                while nlri_offset < nlri_length:
                        tlv_type, tlv_length, tlv_value = decode_tlv(data, nlri_offset, 2, 2)
                        
                        if tlv_type == LSTLV.LOCAL_NODE_DESCRIPTORS:
                                node_length = tlv_length
                                node_offset = nlri_offset + 4
                                node_cur_pos = 0
                                while node_cur_pos < node_length:
                                        node_tlv_type, node_tlv_length, node_tlv_value = decode_tlv(data, node_offset, 2, 2)
                                        if node_tlv_type == LSTLV.IGP_ROUTER_ID:
                                                local_node_id = str(IP.unpack(node_tlv_value))
                                        if node_tlv_type == LSTLV.ASN:
                                                local_asn = str(int(binascii.hexlify(node_tlv_value), 16))
                                        node_offset = node_offset+2+2+node_tlv_length
                                        node_cur_pos = node_cur_pos+2+2+node_tlv_length
                                        
                        if tlv_type == LSTLV.REMOTE_NODE_DESCRIPTORS:
                                node_length = tlv_length
                                node_offset = nlri_offset + 4
                                node_cur_pos = 0
                                while node_cur_pos < node_length:
                                        node_tlv_type, node_tlv_length, node_tlv_value = decode_tlv(data, node_offset, 2, 2)
                                        if node_tlv_type == LSTLV.IGP_ROUTER_ID:
                                                print str(int(binascii.hexlify(node_tlv_value), 16))
                                                remote_node_id = str(IP.unpack(node_tlv_value))
                                        if node_tlv_type == LSTLV.ASN:
                                                remote_asn = str(int(binascii.hexlify(node_tlv_value), 16))
                                        node_offset = node_offset+2+2+node_tlv_length
                                        node_cur_pos = node_cur_pos+2+2+node_tlv_length
                                        
                        if tlv_type == LSTLV.LOCAL_IPV4:
                                local_ipv4 = str(IP.unpack(tlv_value))

                        if tlv_type == LSTLV.REMOTE_IPV4:
                                remote_ipv4 = str(IP.unpack(tlv_value))

                        nlri_offset = nlri_offset+2+2+tlv_length
                        nlri_cur_pos = nlri_cur_pos +2+2+tlv_length
                
                nlri = cls(local_node_id, local_asn, remote_node_id, remote_asn, local_ipv4, remote_ipv4, action)
                nlri.action = action
                if action == 1:
                    nlri.nexthop = IP.unpack(nexthop)
                return len(data), nlri
                
