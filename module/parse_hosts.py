def parse_hosts(input_file):
    hosts = []

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
                    hosts.append(current_host)

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
                    hosts.append(current_host)
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
            hosts.append(current_host)

    return hosts