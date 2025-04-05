import re

def parse_interfaces(input_file):
    interfaces = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        interface_config_started = False
        current_interface = None
        current_interface_data = None
        in_secondary_block = False
        in_ipv6_block = False
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of interface configuration block
            if stripped_line == "config system interface":
                interface_config_started = True
                indentation_level = current_indentation
                continue

            # End of interface configuration block
            if interface_config_started and current_indentation == indentation_level and stripped_line == "end":
                interface_config_started = False
                continue

            if not interface_config_started:
                continue

            # Processing lines in the interface configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new interface block
                if current_interface_data:
                    interfaces.append(current_interface_data)

                interface_name = stripped_line[5:].strip().strip('"')
                current_interface = interface_name
                current_interface_data = {
                    "Interface": interface_name,
                    "Alias": "",
                    "Vdom": "",
                    "Adresse IPv4": "",
                    "NetMask": "",
                    "Adresse IPv6": "",
                    "Distance Administrative": "", 
                    "VLAN ID": "",
                    "Ip Secondaire": "",
                    "Accès IPv4": "",
                    "Accès IPv6": "",
                    "Mode": "", 
                    "Rôle": "",
                    "Type": "",
                    "Membre": "",
                    "Tag": "",
                    "Description": ""
                }
                in_secondary_block = False
                in_ipv6_block = False
                continue

            # End of an interface block
            if current_interface and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_interface_data:
                    interfaces.append(current_interface_data)
                current_interface = None
                current_interface_data = None
                in_secondary_block = False
                in_ipv6_block = False
                continue

            # Processing interface parameters
            if current_interface and current_interface_data:
                # Start of secondary IP block
                if current_indentation == indentation_level + 8 and stripped_line == "config secondaryip":
                    in_secondary_block = True
                    continue

                # End of secondary IP block
                if in_secondary_block and current_indentation == indentation_level + 8 and stripped_line == "end":
                    in_secondary_block = False
                    continue

                # Start of IPv6 block
                if current_indentation == indentation_level + 8 and stripped_line == "config ipv6":
                    in_ipv6_block = True
                    continue

                # End of IPv6 block
                if in_ipv6_block and current_indentation == indentation_level + 8 and stripped_line == "end":
                    in_ipv6_block = False
                    continue

                # Extraction of secondary IPs
                if in_secondary_block and current_indentation == indentation_level + 16 and stripped_line.startswith("set ip "):
                    parts = stripped_line[7:].split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mask = parts[1]
                        if current_interface_data["Ip Secondaire"]:
                            current_interface_data["Ip Secondaire"] += f" ; {ip} {mask}"
                        else:
                            current_interface_data["Ip Secondaire"] = f"{ip} {mask}"
                    continue

                # Extraction of IPv6 information
                if in_ipv6_block and current_indentation == indentation_level + 12:
                    if stripped_line.startswith("set ip6-address "):
                        ipv6_address = stripped_line[15:].strip()
                        if current_interface_data["Adresse IPv6"]:
                            current_interface_data["Adresse IPv6"] += f" ; {ipv6_address}"
                        else:
                            current_interface_data["Adresse IPv6"] = ipv6_address
                    elif stripped_line.startswith("set ip6-allowaccess "):
                        ipv6_access = stripped_line[19:].strip()
                        if current_interface_data["Accès IPv6"]:
                            current_interface_data["Accès IPv6"] += f" ; {ipv6_access}"
                        else:
                            current_interface_data["Accès IPv6"] = ipv6_access
                    continue

                # Standard interface parameters (not in secondaryip or ipv6 block)
                if not in_secondary_block and not in_ipv6_block and current_indentation == indentation_level + 8:
                    if stripped_line.startswith("set vdom "):
                        current_interface_data["Vdom"] = stripped_line[9:].strip().strip('"')
                    elif stripped_line.startswith("set ip "):
                        parts = stripped_line[7:].split()
                        if len(parts) >= 2:
                            current_interface_data["Adresse IPv4"] = parts[0]
                            current_interface_data["NetMask"] = parts[1]
                    elif stripped_line.startswith("set distance"):
                        current_interface_data["Distance Administrative"] = stripped_line[12:].strip().strip('"')
                    elif stripped_line.startswith("set vlanid "):
                        current_interface_data["VLAN ID"] = stripped_line[11:].strip()
                        # If a VLAN ID is defined, automatically set the type to "Vlan"
                        current_interface_data["Type"] = "Vlan"
                    elif stripped_line.startswith("set allowaccess "):
                        current_interface_data["Accès IPv4"] = stripped_line[15:].strip()
                    elif stripped_line.startswith("set mode"): 
                        current_interface_data["Mode"] = stripped_line[9:].strip().strip('"') 
                    elif stripped_line.startswith("set role "):
                        current_interface_data["Rôle"] = stripped_line[9:].strip()
                    elif stripped_line.startswith("set type ") and not current_interface_data["VLAN ID"]:
                        # Only set the type if there is not already a VLAN ID (which would have set the type to "Vlan")
                        current_interface_data["Type"] = stripped_line[9:].strip()
                    elif stripped_line.startswith("set member "):
                        # Extract members without quotes
                        members = re.findall(r'"([^"]+)"', stripped_line[11:])
                        if members:
                            current_interface_data["Membre"] = " ; ".join(members)
                        else:
                            current_interface_data["Membre"] = stripped_line[11:].strip()
                    elif stripped_line.startswith("set description "):
                        current_interface_data["Description"] = stripped_line[16:].strip().strip('"')
                    elif stripped_line.startswith("set alias"):
                        current_interface_data["Alias"] = stripped_line[10:].strip().strip('"')
                    elif stripped_line.startswith("set interface "):
                        parent_interface = stripped_line[13:].strip().strip('"')
                        # Temporarily store the parent interface to associate VLAN tag
                        current_interface_data["_parent_interface"] = parent_interface

        # Add the last interface if it hasn't been added
        if current_interface_data:
            interfaces.append(current_interface_data)

        # Associate VLAN tags with parent interfaces
        for interface in interfaces:
            if interface.get("VLAN ID") and interface.get("_parent_interface"):
                parent_name = interface.get("_parent_interface")
                vlan_id = interface.get("VLAN ID")
                for parent in interfaces:
                    if parent.get("Interface") == parent_name:
                        if parent.get("Tag"):
                            parent["Tag"] += f" ; {vlan_id}"
                        else:
                            parent["Tag"] = vlan_id
                        break

            # Clean up the temporary property
            if "_parent_interface" in interface:
                del interface["_parent_interface"]

    return interfaces