import re

def parse_address_groups(input_file):
    address_groups = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        group_config_started = False
        current_group = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of address group configuration block (first level)
            if current_indentation == 0 and stripped_line == "config firewall addrgrp":
                group_config_started = True
                indentation_level = current_indentation
                continue

            # End of address group configuration block (first level)
            if group_config_started and current_indentation == indentation_level and stripped_line == "end":
                group_config_started = False
                continue

            if not group_config_started:
                continue

            # Processing lines in group configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new group block
                if current_group:
                    address_groups.append(current_group)

                group_name = stripped_line[5:].strip().strip('"')
                current_group = {
                    "Groupe": group_name,
                    "UUID": "",
                    "Membre": ""
                }
                continue

            # End of a group block
            if current_group and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_group:
                    address_groups.append(current_group)
                current_group = None
                continue

            # Processing group parameters
            if current_group and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set uuid "):
                    current_group["UUID"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set member "):
                    # Extract members without quotes
                    members = re.findall(r'"([^"]+)"', stripped_line[11:])
                    if members:
                        current_group["Membre"] = " ; ".join(members)
                    else:
                        current_group["Membre"] = stripped_line[11:].strip()

        # Add the last group if it hasn't been added
        if current_group:
            address_groups.append(current_group)

    return address_groups