import re

def parse_ipsec_phase1(input_file):
    phase1_configs = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        phase1_config_started = False
        current_phase1 = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of IPsec phase1-interface configuration block (first level)
            if current_indentation == 0 and stripped_line == "config vpn ipsec phase1-interface":
                phase1_config_started = True
                indentation_level = current_indentation
                continue

            # End of IPsec phase1-interface configuration block (first level)
            if phase1_config_started and current_indentation == indentation_level and stripped_line == "end":
                phase1_config_started = False
                continue

            if not phase1_config_started:
                continue

            # Processing lines in phase1 configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new phase1 configuration block
                if current_phase1:
                    phase1_configs.append(current_phase1)

                phase1_name = stripped_line[5:].strip().strip('"')
                current_phase1 = {
                    "Source Name": phase1_name,
                    "Interface": "",
                    "KeyLife": "",
                    "Peertype": "",
                    "Algorithme": "",
                    "Remote Adresse": "",
                    "Name Phase 2": "",
                    "Réseaux Source Phase 2": "",
                    "Réseaux Destination Phase 2": ""
                }
                continue

            # End of a phase1 configuration block
            if current_phase1 and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_phase1:
                    phase1_configs.append(current_phase1)
                current_phase1 = None
                continue

            # Processing phase1 parameters
            if current_phase1 and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set interface "):
                    current_phase1["Interface"] = stripped_line[13:].strip().strip('"')
                elif stripped_line.startswith("set keylife "):
                    current_phase1["KeyLife"] = stripped_line[11:].strip()
                elif stripped_line.startswith("set peertype "):
                    current_phase1["Peertype"] = stripped_line[13:].strip()
                elif stripped_line.startswith("set proposal "):
                    current_phase1["Algorithme"] = stripped_line[13:].strip()
                elif stripped_line.startswith("set remote-gw "):
                    current_phase1["Remote Adresse"] = stripped_line[14:].strip()

        # Add the last phase1 configuration if it hasn't been added
        if current_phase1:
            phase1_configs.append(current_phase1)

    return phase1_configs

def parse_ipsec_phase2(input_file, phase1_configs):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        phase2_config_started = False
        current_phase2 = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of IPsec phase2-interface configuration block (first level)
            if current_indentation == 0 and stripped_line == "config vpn ipsec phase2-interface":
                phase2_config_started = True
                indentation_level = current_indentation
                continue

            # End of IPsec phase2-interface configuration block (first level)
            if phase2_config_started and current_indentation == indentation_level and stripped_line == "end":
                phase2_config_started = False
                continue

            if not phase2_config_started:
                continue

            # Processing lines in phase2 configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new phase2 configuration block
                phase2_name = stripped_line[5:].strip().strip('"')
                current_phase2 = {
                    "Name Phase 2": phase2_name,
                    "Réseaux Source Phase 2": "",
                    "Réseaux Destination Phase 2": ""
                }
                continue

            # End of a phase2 configuration block
            if current_phase2 and current_indentation == indentation_level + 4 and stripped_line == "next":
                current_phase2 = None
                continue

            # Processing phase2 parameters
            if current_phase2 and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set phase1name "):
                    phase1_name = stripped_line[15:].strip().strip('"')
                    # Find the corresponding phase1 configuration
                    for phase1 in phase1_configs:
                        if phase1["Source Name"] == phase1_name:
                            if current_phase2["Name Phase 2"]:
                                phase1["Name Phase 2"] += f" ; {current_phase2['Name Phase 2']}"
                            else:
                                phase1["Name Phase 2"] = current_phase2["Name Phase 2"]
                elif stripped_line.startswith("set src-subnet "):
                    src_subnet = stripped_line[14:].strip().strip('"')
                    for phase1 in phase1_configs:
                        if phase1["Source Name"] == phase1_name:
                            if phase1["Réseaux Source Phase 2"]:
                                phase1["Réseaux Source Phase 2"] += f" ; {src_subnet}"
                            else:
                                phase1["Réseaux Source Phase 2"] = src_subnet
                elif stripped_line.startswith("set dst-subnet "):
                    dst_subnet = stripped_line[14:].strip().strip('"')
                    for phase1 in phase1_configs:
                        if phase1["Source Name"] == phase1_name:
                            if phase1["Réseaux Destination Phase 2"]:
                                phase1["Réseaux Destination Phase 2"] += f" ; {dst_subnet}"
                            else:
                                phase1["Réseaux Destination Phase 2"] = dst_subnet