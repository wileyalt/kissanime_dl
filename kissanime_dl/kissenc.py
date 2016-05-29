# -*- coding: utf-8 -*-
# Wiley Yu

try:
	from pkcs7 import PKCS7Encoder
except ImportError:
	from .pkcs7 import PKCS7Encoder

from Crypto.Protocol import KDF
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

#lets cache those values!

#START SHARED

pkc = PKCS7Encoder()

#END SHARED

#START CARTOON

cartoon_hex = "a5e8d2e9c1721ae0e84ad660c472c1f3"
cartoon_k = cartoon_hex.decode('hex')
cartoon_g = "WrxLl3rnA48iafgCy"
cartoon_h = "CartKS$2141#"
cartoon_l = KDF.PBKDF2(cartoon_g, cartoon_h)
cartoon_i = AES.new(cartoon_l, AES.MODE_CBC, cartoon_k)

#END CARTOON

#START ASIAN

#in 256
asian_sha = "m5hSrOWimSmb4Y5I3"
asian_obj_sha = SHA256.new(asian_sha)
asian_a = asian_obj_sha.hexdigest().decode('hex')
asian_c = "32b812e9a1321ae0e84af660c4722b3a"
asian_f = asian_c.decode('hex')
asian_g = AES.new(asian_a, AES.MODE_CBC, asian_f)

#END ASIAN

def kissencCartoon(raw_str):
	jj = raw_str.decode('base64')
	filled = cartoon_i.decrypt(jj)
	
	return pkc.decode(filled)

def kissencAsian(raw_str):
	jj = raw_str.decode('base64')

	filled = asian_g.decrypt(jj)
	return pkc.decode(filled)

