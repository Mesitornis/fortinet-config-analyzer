def parse_virtual_ips(input_file):
    virtual_ips = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        vip_config_started = False
        current_vip = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of Virtual IP configuration block (first level)
            if current_indentation == 0 and stripped_line == "config firewall vip":
                vip_config_started = True
                indentation_level = current_indentation
                continue

            # End of Virtual IP configuration block (first level)
            if vip_config_started and current_indentation == indentation_level and stripped_line == "end":
                vip_config_started = False
                continue

            if not vip_config_started:
                continue

            # Processing lines in VIP configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new VIP block
                if current_vip:
                    virtual_ips.append(current_vip)

                vip_name = stripped_line[5:].strip().strip('"')
                current_vip = {
                    "Name": vip_name,
                    "UUID": "",
                    "External IP": "",
                    "Map IP": "",
                    "External Port": "",
                    "Map Port": "",
                    "External Interface": "",
                    "Port Forward": ""
                }
                continue

            # End of a VIP block
            if current_vip and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_vip:
                    virtual_ips.append(current_vip)
                current_vip = None
                continue

            # Processing VIP parameters
            if current_vip and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set uuid "):
                    current_vip["UUID"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set extip "):
                    current_vip["External IP"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set mappedip "):
                    current_vip["Map IP"] = stripped_line[12:].strip().strip('"')
                elif stripped_line.startswith("set extport "):
                    current_vip["External Port"] = stripped_line[11:].strip()
                elif stripped_line.startswith("set mappedport "):
                    current_vip["Map Port"] = stripped_line[14:].strip()
                elif stripped_line.startswith("set extintf "):
                    current_vip["External Interface"] = stripped_line[11:].strip().strip('"')
                elif stripped_line.startswith("set portforward "):
                    current_vip["Port Forward"] = stripped_line[15:].strip()

        # Add the last VIP if it hasn't been added
        if current_vip:
            virtual_ips.append(current_vip)

    return virtual_ips