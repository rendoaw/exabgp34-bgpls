# encoding: utf-8
"""
linkstate.py

Created by Rendo Wibawa on 2016-06-26.
"""


from struct import unpack

from exabgp.protocol.ip import NoIP
from exabgp.protocol.family import AFI
from exabgp.protocol.family import SAFI
from exabgp.protocol.ip.address import Address

from exabgp.bgp.message import IN
from exabgp.bgp.message.update.attribute.attribute import Attribute
from exabgp.bgp.message.update.nlri.nlri import NLRI

from exabgp.bgp.message.notification import Notify
from exabgp.bgp.message.open.capability.negotiated import Negotiated

from exabgp.protocol.ip import IP
import binascii

def decode_tlv(data, offset, type_len, length_len):
	t, = unpack('!H',data[offset:offset+type_len])
	l, = unpack('!H',data[offset+type_len:offset+type_len+length_len])
	v = data[offset+type_len+length_len:offset+type_len+length_len+l]
	return (t,l,v)


class LinkState(Attribute):
	FLAG = Attribute.Flag.OPTIONAL
	ID = Attribute.CODE.LINK_STATE

	def __init__ (self, ls_attributes):
		self.ls_attributes = ls_attributes

	def packed_attributes (self):
		return

	def pack (self, addpath):
		return ''.join(self.packed_attributes(addpath,Negotiated.FREE_SIZE))

	def __len__ (self):
		raise RuntimeError('we can not give you the size of an MPRNLRI - was it with our witout addpath ?')
		# return len(self.pack(False))

	def __str__ (self):
		txt = ""
		for k in sorted(self.ls_attributes):
			if isinstance(self.ls_attributes[k], str):
				if self.ls_attributes[k] == "":
					continue
				txt = txt+" "+k+" "+self.ls_attributes[k]
			if isinstance(self.ls_attributes[k], int) or isinstance(self.ls_attributes[k], float):
				if self.ls_attributes[k] == -1:
					continue
				txt = txt+" "+k+" "+str(self.ls_attributes[k])
			if isinstance(self.ls_attributes[k], dict):
				if len(self.ls_attributes[k]) == 0:
					continue
				txt = txt+" "+k+"{"
				for i in sorted(self.ls_attributes[k]):
					txt = txt+" ["+str(i)+"] "+str(self.ls_attributes[k][i])
				txt = txt+" }"
		return "LinkState: "+txt

	@classmethod
	def unpack (cls, data, negotiated):
		ls_attributes = {}
		ls_attributes['hostname'] = ""
		ls_attributes['available_bw'] = {}
		ls_attributes['isis_area_id'] = ""
		ls_attributes['ipv4_router_id'] = ""
		ls_attributes['admin_group'] = ""
		ls_attributes['max_link_bw'] = -1
		ls_attributes['max_resv_bw'] = -1
		ls_attributes['te_metric'] = -1
		ls_attributes['metric'] = -1
		#print "data = "+ binascii.hexlify(bytearray(data))
		offset = 0
		while offset < len(data):
			t, l, v = decode_tlv(data, offset, 2, 2)
			if t == 1026:
				ls_attributes['hostname'] = str(v)
			if t == 1027:
				ls_attributes['isis_area_id'] = str(binascii.hexlify(v))
			if t == 1028:
				ls_attributes['ipv4_router_id'] = str(IP.unpack(v))
			if t == 1088:
				ls_attributes['admin_group'] = str(binascii.hexlify(v))
			if t == 1089:
				ls_attributes['max_link_bw'] = str(int(binascii.hexlify(v), 16))
			if t == 1090:
				ls_attributes['max_resv_bw'] = str(int(binascii.hexlify(v), 16))
			if t == 1091:
				ls_attributes['available_bw'][0] = str(int(binascii.hexlify(v)[0:4], 16))
				ls_attributes['available_bw'][1] = str(int(binascii.hexlify(v)[4:8], 16))
				ls_attributes['available_bw'][2] = str(int(binascii.hexlify(v)[8:12], 16))
				ls_attributes['available_bw'][3] = str(int(binascii.hexlify(v)[12:16], 16))
				ls_attributes['available_bw'][4] = str(int(binascii.hexlify(v)[16:20], 16))
				ls_attributes['available_bw'][5] = str(int(binascii.hexlify(v)[20:24], 16))
				ls_attributes['available_bw'][6] = str(int(binascii.hexlify(v)[24:28], 16))
				ls_attributes['available_bw'][7] = str(int(binascii.hexlify(v)[28:32], 16))
			if t == 1092:
				ls_attributes['te_metric'] = str(int(binascii.hexlify(v), 16))
			if t == 1095:
				ls_attributes['metric'] = str(int(binascii.hexlify(v), 16))
			offset = offset + l + 2 + 2
		return cls(ls_attributes)

