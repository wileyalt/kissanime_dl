# -*- coding: utf-8 -*-
# Wiley Yu

try:
	from pkcs7 import PKCS7Encoder
except ImportError:
	from .pkcs7 import PKCS7Encoder

from Crypto.Protocol import KDF
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import requests
import binascii
import base64

#lets cache those values!

#START SHARED

pkc = PKCS7Encoder()

#END SHARED

#START CARTOON

cartoon_hex = "a5e8d2e9c1721ae0e84ad660c472c1f3".encode('utf8')
cartoon_k = binascii.unhexlify(cartoon_hex)
cartoon_g = "WrxLl3rnA48iafgCy".encode('utf8')
cartoon_h = "CartKS$2141#".encode('utf8')
cartoon_l = KDF.PBKDF2(cartoon_g, cartoon_h)

#END CARTOON

#START ASIAN

asian_c = "32b812e9a1321ae0e84af660c4722b3a".encode('utf8')
asian_f = binascii.unhexlify(asian_c)

#assumes site domain is kissasian.com
asian_topost = 'http://kissasian.com/External/RSK'
asian_headers = {
	'X-Requested-With': 'XMLHttpRequest'
}

#END ASIAN

def kissencCartoon(raw_str):
	cartoon_i = AES.new(cartoon_l, AES.MODE_CBC, cartoon_k)
	jj = base64.b64decode(raw_str)
	filled = cartoon_i.decrypt(jj)
	
	return pkc.decode(filled).decode('utf8')

def kissencAsian(raw_str, sess):
	#requires a session because the js makes an ajax request
    #in 256
	post_data = sess.post(asian_topost, headers=asian_headers)
	asian_sha = post_data.text.encode('utf8')
	asian_obj_sha = SHA256.new(asian_sha)
	asian_a = binascii.unhexlify(asian_obj_sha.hexdigest() )

	asian_g = AES.new(asian_a, AES.MODE_CBC, asian_f)
	jj = base64.b64decode(raw_str)

	filled = asian_g.decrypt(jj)
	return pkc.decode(filled).decode('utf8')

def kissencAnime(raw_str):
	return base64.b64decode(raw_str).decode('utf8')

