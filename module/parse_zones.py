import re

def parse_zones(input_file, interfaces):
    zones = []
    interface_to_zone = {}

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        zone_config_started = False
        current_zone = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of zone configuration block (first level)
            if current_indentation == 0 and stripped_line == "config system zone":
                zone_config_started = True
                indentation_level = current_indentation
                continue

            # End of zone configuration block (first level)
            if zone_config_started and current_indentation == indentation_level and stripped_line == "end":
                zone_config_started = False
                continue

            if not zone_config_started:
                continue

            # Processing lines in zone configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new zone block
                if current_zone:
                    zones.append(current_zone)

                zone_name = stripped_line[5:].strip().strip('"')
                current_zone = {
                    "Zone": zone_name,
                    "Membre": ""
                }
                continue

            # End of a zone block
            if current_zone and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_zone:
                    zones.append(current_zone)
                current_zone = None
                continue

            # Processing zone parameters
            if current_zone and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set interface "):
                    # Extract interfaces without quotes
                    interfaces_list = re.findall(r'"([^"]+)"', stripped_line[14:])
                    if interfaces_list:
                        current_zone["Membre"] = ", ".join(interfaces_list)
                        for interface in interfaces_list:
                            interface_to_zone[interface] = current_zone["Zone"]
                    else:
                        interface_name = stripped_line[14:].strip()
                        current_zone["Membre"] = interface_name
                        interface_to_zone[interface_name] = current_zone["Zone"]

    # Now update interfaces with zone information
    for interface in interfaces:
        interface_name = interface.get("Interface")
        if interface_name in interface_to_zone:
            interface["Zone"] = interface_to_zone[interface_name]

    return zones
