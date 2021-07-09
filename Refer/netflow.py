import re, time

# def get_net_info():
flow1 = open('/proc/net/dev')
lines = flow1.read()
flow1.close()
r_eth0 = re.compile('eth0:(.*)\s')
r_wlan0 = re.compile('wlan0:(.*)\s')
print(r_wlan0)
match_eth0 = r_eth0.findall(lines)
match_wlan0 = r_wlan0.findall(lines)
print(match_wlan0, match_eth0)
    # return (match_eth0,match_wlan0)
# def getflow():
#     #tiqu xinxi
#     #print g