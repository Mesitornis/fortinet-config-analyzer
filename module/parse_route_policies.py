import re

def parse_route_policies(input_file):
    route_policies = []

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

            # Start of route policy configuration block (first level)
            if current_indentation == 0 and stripped_line == "config router policy":
                policy_config_started = True
                indentation_level = current_indentation
                continue

            # End of route policy configuration block (first level)
            if policy_config_started and current_indentation == indentation_level and stripped_line == "end":
                policy_config_started = False
                continue

            if not policy_config_started:
                continue

            # Processing lines in route policy configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new route policy block
                if current_policy:
                    route_policies.append(current_policy)

                current_policy = {
                    "Source Interface": "",
                    "Destination Interface": "",
                    "Source Adresse": "",
                    "Destination Adresse": "",
                    "Start Port": "",
                    "End Port": "",
                    "Gateway": "",
                    "Status": "enable",
                    "Action": "allow"
                }
                continue

            # End of a route policy block
            if current_policy and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_policy:
                    route_policies.append(current_policy)
                current_policy = None
                continue

            # Processing route policy parameters
            if current_policy and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set input-device "):
                    current_policy["Source Interface"] = stripped_line[17:].strip().strip('"')
                elif stripped_line.startswith("set output-device "):
                    current_policy["Destination Interface"] = stripped_line[18:].strip().strip('"')
                elif stripped_line.startswith("set src "):
                    addresses = re.findall(r'"([^"]+)"', stripped_line[8:])
                    current_policy["Source Adresse"] = ", ".join(addresses)
                elif stripped_line.startswith("set dst "):
                    addresses = re.findall(r'"([^"]+)"', stripped_line[8:])
                    current_policy["Destination Adresse"] = ", ".join(addresses)
                elif stripped_line.startswith("set start-port "):
                    current_policy["Start Port"] = stripped_line[14:].strip().strip('"')
                elif stripped_line.startswith("set end-port "):
                    current_policy["End Port"] = stripped_line[12:].strip().strip('"')
                elif stripped_line.startswith("set gateway "):
                    current_policy["Gateway"] = stripped_line[11:].strip().strip('"')
                elif stripped_line.startswith("set status "):
                    current_policy["Status"] = stripped_line[11:].strip()
                elif stripped_line.startswith("set action "):
                    current_policy["Action"] = stripped_line[11:].strip()

        # Add the last route policy if it hasn't been added
        if current_policy:
            route_policies.append(current_policy)

    return route_policies