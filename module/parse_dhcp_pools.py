import re

def parse_dhcpV4_pools(input_file):
    dhcpv4_pools = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        dhcp_config_started = False
        current_dhcp_pool = None
        in_range_block = False
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Déterminer le niveau d'indentation en comptant les espaces au début de la ligne
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Début du bloc de configuration DHCP
            if stripped_line == "config system dhcp server":
                dhcp_config_started = True
                indentation_level = current_indentation
                continue

            # Fin du bloc de configuration DHCP
            if dhcp_config_started and current_indentation == indentation_level and stripped_line == "end":
                dhcp_config_started = False
                continue

            if not dhcp_config_started:
                continue

            # Traitement des lignes dans le bloc de configuration DHCP
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Début d'un nouveau bloc DHCP Pool
                if current_dhcp_pool:
                    dhcpv4_pools.append(current_dhcp_pool)

                current_dhcp_pool = {
                    "Interface": "",
                    "Domaine": "",
                    "Gateway": "",
                    "NetMask": "",
                    "Start Pool": "",
                    "End Pool": "",
                    "DNS": ""
                }
                in_range_block = False
                continue

            # Fin d'un bloc DHCP Pool
            if current_dhcp_pool and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_dhcp_pool:
                    dhcpv4_pools.append(current_dhcp_pool)
                current_dhcp_pool = None
                in_range_block = False
                continue

            # Traitement des paramètres du DHCP Pool
            if current_dhcp_pool:
                # Début du bloc range DHCP
                if current_indentation == indentation_level + 8 and stripped_line == "config ip-range":
                    in_range_block = True
                    continue

                # Fin du bloc range DHCP
                if in_range_block and current_indentation == indentation_level + 8 and stripped_line == "end":
                    in_range_block = False
                    continue

                # Extraction des IP dans le bloc range DHCP
                if in_range_block and current_indentation == indentation_level + 16:
                    if stripped_line.startswith("set start-ip"):
                        current_dhcp_pool["Start Pool"] = stripped_line[12:].strip()
                    elif stripped_line.startswith("set end-ip"):
                        current_dhcp_pool["End Pool"] = stripped_line[10:].strip()

                # Paramètres standard du DHCP Pool (non dans le bloc range)
                if not in_range_block and current_indentation == indentation_level + 8:
                    if stripped_line.startswith("set interface"):
                        current_dhcp_pool["Interface"] = stripped_line[14:].strip().strip('"')
                    elif stripped_line.startswith("set domain"):
                        current_dhcp_pool["Domaine"] = stripped_line[11:].strip().strip('"')
                    elif stripped_line.startswith("set default-gateway"):
                        current_dhcp_pool["Gateway"] = stripped_line[19:].strip()
                    elif stripped_line.startswith("set netmask"):
                        current_dhcp_pool["NetMask"] = stripped_line[11:].strip()
                    elif stripped_line.startswith("set dns-server"):
                        current_dhcp_pool["DNS"] = stripped_line[15:].strip()

    return dhcpv4_pools

def parse_dhcpv6_pools(input_file):
    dhcpv6_pools = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        dhcp6_config_started = False
        current_pool = None
        indentation_level = 0

        # Regex to match set dns-server followed by a number
        dns_regex = re.compile(r"^set dns-server\d* ")

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of DHCPv6 configuration block (first level)
            if current_indentation == 0 and stripped_line == "config system dhcp6 server":
                dhcp6_config_started = True
                indentation_level = current_indentation
                continue

            # End of DHCPv6 configuration block (first level)
            if dhcp6_config_started and current_indentation == indentation_level and stripped_line == "end":
                dhcp6_config_started = False
                continue

            if not dhcp6_config_started:
                continue

            # Processing lines in DHCPv6 configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new DHCPv6 pool block
                if current_pool:
                    dhcpv6_pools.append(current_pool)

                current_pool = {
                    "Interface": "",
                    "Network": "",
                    "Start Pool": "",
                    "End Pool": "",
                    "DNS": ""
                }
                continue

            # End of a DHCPv6 pool block
            if current_pool and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_pool:
                    dhcpv6_pools.append(current_pool)
                current_pool = None
                continue

            # Processing pool parameters
            if current_pool:
                if current_indentation == indentation_level + 8:
                    if stripped_line.startswith("set interface "):
                        current_pool["Interface"] = stripped_line.split()[2].strip().strip('"')
                    elif stripped_line.startswith("set subnet "):
                        current_pool["Network"] = stripped_line.split()[2].strip()

                if current_indentation == indentation_level + 16:
                    if stripped_line.startswith("set start-ip "):
                        current_pool["Start Pool"] = stripped_line.split()[2].strip()
                    elif stripped_line.startswith("set end-ip "):
                        current_pool["End Pool"] = stripped_line.split()[2].strip()

                if current_indentation == indentation_level + 8 and dns_regex.match(stripped_line):
                    dns_server = stripped_line.split()[2].strip()
                    if current_pool["DNS"]:
                        current_pool["DNS"] += f" ; {dns_server}"
                    else:
                        current_pool["DNS"] = dns_server

    return dhcpv6_pools