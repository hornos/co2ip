#!/usr/bin/env python

import time, csv, sys, socket, struct
import sqlite3

def dottedQuadToNum(ip):
  return struct.unpack('!L',socket.inet_aton(ip))[0]

def numToDottedQuad(n):
  return socket.inet_ntoa(struct.pack('!L',n))

def makeMask(n):
  return (2L<<n-1)-1

def ipToNetAndHost(ip, maskbits):
  n = dottedQuadToNum(ip)
  m = makeMask(maskbits)
  host = n & m
  net = n - host
  return numToDottedQuad(net), numToDottedQuad(host)
# end

def iprange(startip, endip):
  bits = 1
  mask = 1
  while bits < 32 :
    newip = startip | mask
    if (newip>endip) or (((startip>>bits) << bits) != startip) :
      bits = bits - 1
      mask = mask >> 1
      break
    bits = bits + 1
    mask = (mask<<1) + 1
  newip = startip | mask
  bits = 32 - bits
  return "%s/%d" % (numToDottedQuad(startip), bits)
  if newip < endip : 
    iprange(newip + 1, endip)
# end                                                                                                                                                                                                       printrange(newip + 1, endip)

### main
# IP FROM      IP TO        REGISTRY  ASSIGNED   CTRY CNTRY COUNTRY
# "1346797568","1346801663","ripencc","20010601","il","isr","Israel"
# (ipfrom text, ipto text, registry text, assigned text, ctry text, cntry text, country text)

if __name__ == '__main__':
  # conn = sqlite3.connect(':memory:')
  conn = sqlite3.connect(sys.argv[1])
  c = conn.cursor()
  cc = conn.cursor()

  # select * from ip2country where ctry in (select distinct ctry from ip2country order by ctry) order by ctry;
  for ctry in c.execute('SELECT DISTINCT ctry FROM ip2country order by ctry'):
    zfn = str(ctry[0]).lower() + ".zone"
    print "Generating zone file: "+zfn
    with open(zfn, 'w+') as zone:
      zone.truncate()

      for row in cc.execute('SELECT * FROM ip2country WHERE ctry = "'+str(ctry[0])+'"'):
        zone.write( iprange(dottedQuadToNum(str(row[0])), dottedQuadToNum(str(row[1]))) + "\n")

  conn.close()
