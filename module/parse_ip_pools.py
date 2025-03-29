def parse_ip_pools(input_file):
    ip_pools = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        ip_pool_config_started = False
        current_ip_pool = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of IP pool configuration block (first level)
            if current_indentation == 0 and stripped_line == "config firewall ippool":
                ip_pool_config_started = True
                indentation_level = current_indentation
                continue

            # End of IP pool configuration block (first level)
            if ip_pool_config_started and current_indentation == indentation_level and stripped_line == "end":
                ip_pool_config_started = False
                continue

            if not ip_pool_config_started:
                continue

            # Processing lines in IP pool configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new IP pool block
                if current_ip_pool:
                    ip_pools.append(current_ip_pool)

                pool_name = stripped_line[5:].strip().strip('"')
                current_ip_pool = {
                    "Name": pool_name,
                    "Type": "",
                    "Start IP": "",
                    "End IP": "",
                    "Source Start IP": "",
                    "Source End IP": "",
                    "ARP": "enable"
                }
                continue

            # End of an IP pool block
            if current_ip_pool and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_ip_pool:
                    ip_pools.append(current_ip_pool)
                current_ip_pool = None
                continue

            # Processing IP pool parameters
            if current_ip_pool and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set type "):
                    current_ip_pool["Type"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set startip "):
                    current_ip_pool["Start IP"] = stripped_line[11:].strip()
                elif stripped_line.startswith("set endip "):
                    current_ip_pool["End IP"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set source-startip "):
                    current_ip_pool["Source Start IP"] = stripped_line[18:].strip()
                elif stripped_line.startswith("set source-endip "):
                    current_ip_pool["Source End IP"] = stripped_line[16:].strip()
                elif stripped_line.startswith("set arp-reply "):
                    current_ip_pool["ARP"] = stripped_line[13:].strip()

        # Add the last IP pool if it hasn't been added
        if current_ip_pool:
            ip_pools.append(current_ip_pool)

    return ip_pools