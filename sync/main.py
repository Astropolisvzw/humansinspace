import network
import time
import machine
import config

# Import secrets for WiFi credentials
try:
    import secrets
except ImportError:
    print("Error: secrets.py not found!")
    print("Please create sync/secrets.py with SSID and PASSWORD")

# Load configuration
cfg = config.load_config()
update_interval_hours = cfg.get('update_interval_hours', 6)

# Get WiFi networks from both config and secrets
wifi_networks = config.get_wifi_networks()

# Try to connect to WiFi networks in order
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

connected = False
for network_config in wifi_networks:
    ssid = network_config["ssid"]
    password = network_config["password"]

    print(f"Trying to connect to {ssid}...")
    wlan.connect(ssid, password)

    # Wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.isconnected():
            connected = True
            print(f"Connected to {ssid}!")
            break
        max_wait -= 1
        time.sleep(1)

    if connected:
        break
    else:
        print(f"Failed to connect to {ssid}")

if not connected:
    print('Failed to connect to any WiFi network')
    print('Available networks:', [net["ssid"] for net in wifi_networks])

if wlan.isconnected():
    print('Connected to WiFi!')
    ip_address = wlan.ifconfig()[0]
    print('Network config:', wlan.ifconfig())
    print(f'IP Address: {ip_address}')
    print(f'Visit: http://{ip_address}/')

    # Wait a moment for network to fully stabilize
    time.sleep(2)

    # Sync time with NTP server
    import ntptime
    ntptime.set_time()

    # Start web server
    import webserver
    import humansinspace_color

    server = webserver.SimpleWebServer(port=80)
    server.start()
    print(f'Web server started at http://{ip_address}/')
    print(f'API endpoint: http://{ip_address}/api/latest')

    # Check if we need to update the display
    # Track last update time in a file
    try:
        with open('last_update.txt', 'r') as f:
            last_update_time = int(f.read().strip())
    except:
        last_update_time = 0

    current_time = time.time()
    time_since_update = current_time - last_update_time
    update_interval_seconds = update_interval_hours * 3600

    should_update_display = time_since_update >= update_interval_seconds

    if should_update_display:
        print(f'Time to update display (last update: {time_since_update // 3600} hours ago)')
    else:
        remaining_hours = (update_interval_seconds - time_since_update) / 3600
        print(f'Display updated {time_since_update // 60} minutes ago. Next update in {remaining_hours:.1f} hours')

    # Query API and update web server data on first run
    import humansinspace_color
    space_data = humansinspace_color.query_api()
    if space_data:
        timestamp = humansinspace_color.format_timestamp()
        server.set_data(space_data, timestamp)
        num_humans = space_data.get('number', 0)
        print(f'API data fetched: {num_humans} humans in space')

        # Check if data changed (compare with last known value)
        try:
            with open('last_count.txt', 'r') as f:
                last_count = int(f.read().strip())
        except:
            last_count = -1

        if num_humans != last_count or should_update_display:
            if num_humans != last_count:
                print(f'Data changed! {last_count} -> {num_humans}. Updating display...')
            else:
                print(f'Scheduled update after {time_since_update // 3600} hours. Updating display...')

            # Update the e-paper display
            humansinspace_color.display_space_info(web_server=server)

            # Save the count and update time
            with open('last_count.txt', 'w') as f:
                f.write(str(num_humans))
            with open('last_update.txt', 'w') as f:
                f.write(str(int(current_time)))
        else:
            print(f'No change in data ({num_humans} humans). Display not updated to preserve e-paper.')

    # Keep web server running indefinitely
    # Check periodically if we need to update the display
    print('Web server is running. Accessible at all times.')
    print(f'Display will update every {update_interval_hours} hours.')

    last_check_time = time.time()
    check_interval = 60  # Check every minute if we need to update

    while True:
        server.handle_request()
        time.sleep(0.1)

        # Check if it's time to update the display
        current_time = time.time()
        if current_time - last_check_time >= check_interval:
            last_check_time = current_time

            # Check for data changes
            space_data = humansinspace_color.query_api()
            if space_data:
                timestamp = humansinspace_color.format_timestamp()
                server.set_data(space_data, timestamp)
                num_humans = space_data.get('number', 0)

                # Get last known count
                try:
                    with open('last_count.txt', 'r') as f:
                        last_count = int(f.read().strip())
                except:
                    last_count = -1

                # Get last update time
                try:
                    with open('last_update.txt', 'r') as f:
                        last_update_time = int(f.read().strip())
                except:
                    last_update_time = 0

                time_since_update = current_time - last_update_time
                update_interval_seconds = update_interval_hours * 3600
                needs_scheduled_update = time_since_update >= update_interval_seconds

                # Update display if data changed or scheduled update is due
                if num_humans != last_count or needs_scheduled_update:
                    if num_humans != last_count:
                        print(f'Data changed! {last_count} -> {num_humans}. Updating display...')
                    else:
                        print(f'Scheduled update after {time_since_update // 3600} hours. Updating display...')

                    humansinspace_color.display_space_info(web_server=server)

                    # Save the count and update time
                    with open('last_count.txt', 'w') as f:
                        f.write(str(num_humans))
                    with open('last_update.txt', 'w') as f:
                        f.write(str(int(current_time)))

else:
    print('Failed to connect to WiFi')
    print('Check your credentials in secrets.py')
