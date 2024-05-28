from datetime import timedelta, datetime
import psutil

def compute_consumed_data(consumed):
    if "GB" in consumed:
        consumed  = float(consumed.replace('GB', ''))
    elif "MB" in consumed:
        consumed = float(float(consumed.replace('MB', '')) / 1024)
    elif "KB" in consumed:
        consumed = float(float(consumed.replace('KB', '')) / (1024*1024))
    elif "0.00B" in consumed:
        consumed = 0.0
    else:
        consumed = float(float(re.findall(r'[0-9]+\.[0-9]+', consumed)[0].replace('B', '')) / (1024*1024*1024))
    
    return consumed


def compute_consumed_hours(allocated, expirary_date):
        
    allocated       = allocated.split('hrs')[0].rstrip().lstrip()
    now             = datetime.now()
    expirary_date   = datetime.strptime(expirary_date,'%b %d %Y, %I:%M %p')
    sub_date        = expirary_date - timedelta(hours=float(allocated))
    subdelta        = now - sub_date
    remaining_hours = round(float(subdelta.total_seconds())/3600,3)
    consumed        = float(float(allocated) - remaining_hours)
    if consumed < 0:
        consumed = 0
    return round(float(subdelta.total_seconds())/3600,3)

'''
This routine gets any currently received/sent bytes on the tunnel interface
These values are used as a starting point. 
If a user connects to a node, disconnects, and later connects to a different node
the kernel still has in cache the tx/rx bytes for the interface.

So, this routine is used to pick up whatever was cached (if any)
and provide a starting point for the data consumed.
'''
def init_GetConsumedWhileConnected():
    try: 
        bytes_sent = round(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_sent) / 1073741824),3)
        bytes_recvd = round(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_recv) / 1073741824),3)
        
        return {'sent' : bytes_sent, "rcvd" : bytes_recvd}
    except KeyError:
        # Find V2Ray Tunnel (tun2socks) interface
        for iface in psutil.net_if_addrs().keys():
            if "tun" in iface:
                IFACE = iface
                print(IFACE)
                break
        try:     
            bytes_sent = round(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_sent) / 1073741824),3)
            bytes_recvd = round(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_recv) / 1073741824),3)
            
            return {'sent' : bytes_sent, "rcvd" : bytes_recvd}
        except Exception as e:
            print(str(e))
            return {'sent': 0, 'rcvd' : 0}
        
def GetConsumedWhileConnected(sConsumed, Bytes):
    try: 
        bytes_sent = round(float(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_sent) / 1073741824) - Bytes['sent']),3) 
        bytes_recvd = round(float(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_recv) / 1073741824) - Bytes['rcvd']),3)  
        
        total_data = str(round(float(bytes_sent + bytes_recvd)+ float(sConsumed),3)) + "GB"
    except KeyError:
        for iface in psutil.net_if_addrs().keys():
            if "tun" in iface:
                IFACE = iface
                break
            
        try: 
            bytes_sent = round(float(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_sent) / 1073741824) - Bytes['sent']),3) 
            bytes_recvd = round(float(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_recv) / 1073741824) - Bytes['rcvd']),3)  
        
            total_data = str(round(float(bytes_sent + bytes_recvd)+ float(sConsumed),3)) + "GB"
        except Exception as e:
            print(str(e))
            total_data = "0GB"
            
    print("Total Data: %s" % total_data, end=' ')
    return total_data