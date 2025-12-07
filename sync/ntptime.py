import socket
import struct
import utime

# NTP server
NTP_HOST = "pool.ntp.org"
NTP_PORT = 123

# Difference between NTP epoch (1900) and Unix epoch (1970)
NTP_DELTA = 3155673600

def set_time():
    """Sync system time with NTP server"""
    try:
        print("Syncing time with NTP server...")

        # Create NTP request packet
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B  # NTP version 3, mode 3 (client)

        # Send request
        addr = socket.getaddrinfo(NTP_HOST, NTP_PORT)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3)
        s.sendto(ntp_query, addr)

        # Receive response
        msg = s.recv(48)
        s.close()

        # Extract timestamp (seconds since 1900)
        val = struct.unpack("!I", msg[40:44])[0]

        # Convert to Unix timestamp (seconds since 1970)
        unix_timestamp = val - NTP_DELTA

        # Set system time
        # Note: This sets UTC time
        tm = utime.gmtime(unix_timestamp)

        # For Amsterdam (CET/CEST), add 1 hour in winter, 2 hours in summer
        # Simple approximation: use 1 hour offset (CET)
        # For proper DST handling, you'd need more logic
        local_timestamp = unix_timestamp + 3600  # Add 1 hour for CET
        tm = utime.localtime(local_timestamp)

        # Set the RTC
        from machine import RTC
        rtc = RTC()
        rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))

        print(f"Time synced: {tm[3]:02d}:{tm[4]:02d}:{tm[5]:02d}")
        return True

    except Exception as e:
        print(f"Failed to sync time: {e}")
        return False
