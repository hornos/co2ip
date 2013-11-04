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

def printrange(startip, endip):
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
  print "%s/%d" % (numToDottedQuad(startip), bits)
  if newip < endip : 
          printrange(newip + 1, endip)
# end                                                                                                                                                                                                       printrange(newip + 1, endip)

### main
# IP FROM      IP TO        REGISTRY  ASSIGNED   CTRY CNTRY COUNTRY
# "1346797568","1346801663","ripencc","20010601","il","isr","Israel"

if __name__ == '__main__':
  # conn = sqlite3.connect(':memory:')
  conn = sqlite3.connect('ip2country.db')
  c = conn.cursor()
  c.execute('DROP TABLE IF EXISTS ip2country;')
  c.execute('''CREATE TABLE ip2country
               (ipfrom text, ipto text, registry text, assigned text, ctry text, cntry text, country text)''')

  with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    print "Generating database..."
    for row in reader:
      try:
        fromip = numToDottedQuad(int(row[0]))
        toip   = numToDottedQuad(int(row[1]))
        row[3] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(row[3])))
      except:
        print "ERROR: " + str(row)
      # print row
      c.execute("INSERT INTO ip2country VALUES ('"+str(fromip)+"','"+str(toip)+"','"+\
                                                   str(row[2])+"','"+str(row[3])+"','"+\
                                                   str(row[4])+"','"+str(row[5])+"','"+\
                                                   str(row[6]).replace("'", " ")+"')")
      # printrange(int(row[0]), int(row[1]))

      # print ' '.join(row)
    # end for
  # end with

  conn.commit()
  conn.close()
