import re

def parse_firewall_policies(input_file):
    firewall_policies = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        policy_config_started = False
        current_policy = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of firewall policy configuration block (first level)
            if current_indentation == 0 and stripped_line == "config firewall policy":
                policy_config_started = True
                indentation_level = current_indentation
                continue

            # End of firewall policy configuration block (first level)
            if policy_config_started and current_indentation == indentation_level and stripped_line == "end":
                policy_config_started = False
                continue

            if not policy_config_started:
                continue

            # Processing lines in policy configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new policy block
                if current_policy:
                    firewall_policies.append(current_policy)

                policy_name = stripped_line[5:].strip().strip('"')
                current_policy = {
                    "Name": policy_name,
                    "UUID": "",
                    "Source Interface": "",
                    "Destination Interface": "",
                    "Source Adresse": "",
                    "Destination Adresse": "",
                    "Service": "",
                    "Planification": "",
                    "Groupe": "",
                    "User": "",
                    "NAT": "",
                    "IP Pool": "",
                    "Pool Name": "",
                    "Action": "",
                    "Log Traffic": "",
                    "Commentaire": ""
                }
                continue

            # End of a policy block
            if current_policy and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_policy:
                    firewall_policies.append(current_policy)
                current_policy = None
                continue

            # Processing policy parameters
            if current_policy and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set name "):
                    current_policy["Name"] = stripped_line[9:].strip().strip('"')
                elif stripped_line.startswith("set uuid "):
                    current_policy["UUID"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set srcintf "):
                    current_policy["Source Interface"] = stripped_line[12:].strip().strip('"')
                elif stripped_line.startswith("set dstintf "):
                    current_policy["Destination Interface"] = stripped_line[12:].strip().strip('"')
                elif stripped_line.startswith("set srcaddr "):
                    # Remove quotes and join multiple addresses with commas
                    addresses = re.findall(r'"([^"]+)"', stripped_line[11:])
                    current_policy["Source Adresse"] = " ; ".join(addresses)
                elif stripped_line.startswith("set dstaddr "):
                    addresses = re.findall(r'"([^"]+)"', stripped_line[11:])
                    current_policy["Destination Adresse"] = " ; ".join(addresses)
                elif stripped_line.startswith("set service "):
                    services = re.findall(r'"([^"]+)"', stripped_line[11:])
                    current_policy["Service"] = " ; ".join(services)
                elif stripped_line.startswith("set schedule "):
                    current_policy["Planification"] = stripped_line[13:].strip().strip('"')
                elif stripped_line.startswith("set groups "):
                    # Remove quotes and join multiple groups with commas
                    groups = re.findall(r'"([^"]+)"', stripped_line[10:])
                    current_policy["Groupe"] = " ; ".join(groups)
                elif stripped_line.startswith("set users "):
                    # Remove quotes and join multiple users with commas
                    users = re.findall(r'"([^"]+)"', stripped_line[9:])
                    current_policy["User"] = " ; ".join(users)
                elif stripped_line.startswith("set nat "):
                    current_policy["NAT"] = stripped_line[8:].strip()
                elif stripped_line.startswith("set ippool "):
                    current_policy["IP Pool"] = stripped_line[11:].strip()
                elif stripped_line.startswith("set poolname "):
                    current_policy["Pool Name"] = stripped_line[13:].strip().strip('"')
                elif stripped_line.startswith("set action "):
                    current_policy["Action"] = stripped_line[11:].strip()
                elif stripped_line.startswith("set logtraffic "):
                    current_policy["Log Traffic"] = stripped_line[14:].strip()
                elif stripped_line.startswith("set comments "):
                    current_policy["Commentaire"] = stripped_line[13:].strip().strip('"')

        # Add the last policy if it hasn't been added
        if current_policy:
            firewall_policies.append(current_policy)

    return firewall_policies