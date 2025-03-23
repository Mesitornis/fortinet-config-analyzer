def parse_hostsv4(input_file):
    hostsv4 = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        host_config_started = False
        current_host = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of firewall address configuration block (first level)
            if current_indentation == 0 and stripped_line == "config firewall address":
                host_config_started = True
                indentation_level = current_indentation
                continue

            # End of firewall address configuration block (first level)
            if host_config_started and current_indentation == indentation_level and stripped_line == "end":
                host_config_started = False
                continue

            if not host_config_started:
                continue

            # Processing lines in host configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new host block
                if current_host:
                    hostsv4.append(current_host)

                hostname = stripped_line[5:].strip().strip('"')
                current_host = {
                    "Hostname": hostname,
                    "UUID": "",
                    "Interface": "",
                    "Type": "",
                    "MAC": "",
                    "Adresse": "",
                    "NetMask": "",
                    "FQDN": "",
                    "Start IP": "",
                    "End IP": "",
                    "Commentaire": ""
                }
                continue

            # End of a host block
            if current_host and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_host:
                    hostsv4.append(current_host)
                current_host = None
                continue

            # Processing host parameters
            if current_host and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set uuid "):
                    current_host["UUID"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set associated-interface "):
                    current_host["Interface"] = stripped_line[24:].strip().strip('"')
                elif stripped_line.startswith("set type "):
                    parts = stripped_line[9:].strip().split()
                    if parts:
                        current_host["Type"] = parts[0]
                elif stripped_line.startswith("set start-mac "):
                    parts = stripped_line[13:].strip().split()
                    if parts:
                        current_host["MAC"] = parts[0]
                elif stripped_line.startswith("set subnet "):
                    parts = stripped_line[11:].strip().split()
                    if len(parts) >= 2:
                        current_host["Adresse"] = parts[0]
                        current_host["NetMask"] = parts[1]
                elif stripped_line.startswith("set fqdn "):
                    current_host["FQDN"] = stripped_line[9:].strip().strip('"')
                elif stripped_line.startswith("set start-ip "):
                    current_host["Start IP"] = stripped_line[12:].strip()
                elif stripped_line.startswith("set end-ip "):
                    current_host["End IP"] = stripped_line[10:].strip()
                elif stripped_line.startswith("set comment "):
                    current_host["Commentaire"] = stripped_line[11:].strip().strip('"')

        # Add the last host if it hasn't been added
        if current_host:
            hostsv4.append(current_host)

    return hostsv4

def update_hostsv4_with_dhcp(input_file, hostsv4):
    reserved_mac_to_ip = {}

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        dhcp_config_started = False
        current_reservation = None
        reservation_ip = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of DHCP configuration block (first level)
            if current_indentation == 0 and stripped_line == "config system dhcp server":
                dhcp_config_started = True
                indentation_level = current_indentation
                print("Starting DHCP block...")
                continue

            # End of DHCP configuration block (first level)
            if dhcp_config_started and current_indentation == indentation_level and stripped_line == "end":
                dhcp_config_started = False
                print("Ending DHCP block...")
                continue

            if not dhcp_config_started:
                continue

            # Start of reserved-address block (third level)
            if current_indentation == indentation_level + 8 and stripped_line.startswith("edit "):
                current_reservation = None
                reservation_ip = None
                print(f"Starting reserved-address block for reservation {stripped_line}")
                continue

            # End of reserved-address block (third level)
            if current_reservation is not None and current_indentation == indentation_level + 12 and stripped_line == "next": #8 to 12
                if current_reservation and reservation_ip:
                    reserved_mac_to_ip[current_reservation] = reservation_ip
                    print(f"Reserved MAC {current_reservation} with IP {reservation_ip}")
                current_reservation = None
                reservation_ip = None
                continue

            # Processing reserved-address parameters (fourth level)
            if current_indentation == indentation_level + 16:
                if stripped_line.startswith("set mac "):
                    current_reservation = stripped_line.split()[2].strip().strip('"')
                    print(f"Found MAC: {current_reservation}")
                elif stripped_line.startswith("set ip "):
                    reservation_ip = stripped_line.split()[2].strip()
                    print(f"Found IP: {reservation_ip}")

    # Update the hostsv4 with the reserved IP based on MAC
    for host in hostsv4:
        if host.get("Type") == "mac":
            mac_address = host.get("MAC", "").strip()
            if mac_address in reserved_mac_to_ip:
                host["Adresse"] = reserved_mac_to_ip[mac_address]
                print(f"Updated host {host['Hostname']} with IP {host['Adresse']}")

    return hostsv4

def parse_hostsv6(input_file):
    hostv6 = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        host_ipv6_config_started = False
        current_host = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Déterminer le niveau d'indentation en comptant les espaces au début de la ligne
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Début du bloc de configuration des adresses IPv6 (premier niveau)
            if current_indentation == 0 and stripped_line == "config firewall address6":
                host_ipv6_config_started = True
                indentation_level = current_indentation
                continue

            # Fin du bloc de configuration des adresses IPv6 (premier niveau)
            if host_ipv6_config_started and current_indentation == indentation_level and stripped_line == "end":
                host_ipv6_config_started = False
                continue

            if not host_ipv6_config_started:
                continue

            # Traitement des lignes dans le bloc de configuration des adresses IPv6
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Début d'un nouveau bloc d'adresse IPv6
                if current_host:
                    hostv6.append(current_host)

                hostname = stripped_line[5:].strip().strip('"')
                current_host = {
                    "Hostname": hostname,
                    "UUID": "",
                    "Adresse IPv6": ""
                }
                continue

            # Fin d'un bloc d'adresse IPv6
            if current_host and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_host:
                    hostv6.append(current_host)
                current_host = None
                continue

            # Traitement des paramètres de l'adresse IPv6
            if current_host and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set uuid "):
                    current_host["UUID"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set ip6 "):
                    current_host["Adresse IPv6"] = stripped_line[8:].strip()

    return hostv6