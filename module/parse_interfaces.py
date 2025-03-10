import re

def parse_interfaces(input_file):
    interfaces = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        interface_config_started = False
        current_interface = None
        current_interface_data = None
        in_secondary_block = False
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Déterminer le niveau d'indentation en comptant les espaces au début de la ligne
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Début du bloc de configuration des interfaces
            if stripped_line == "config system interface":
                interface_config_started = True
                indentation_level = current_indentation
                continue

            # Fin du bloc de configuration des interfaces
            if interface_config_started and current_indentation == indentation_level and stripped_line == "end":
                interface_config_started = False
                continue

            if not interface_config_started:
                continue

            # Traitement des lignes dans le bloc de configuration des interfaces
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Début d'un nouveau bloc d'interface
                if current_interface_data:
                    interfaces.append(current_interface_data)

                interface_name = stripped_line[5:].strip().strip('"')
                current_interface = interface_name
                current_interface_data = {
                    "Interface": interface_name,
                    "Vdom": "",
                    "Adresse IP": "",
                    "NetMask": "",
                    "VLAN ID": "",
                    "Ip Secondaire": "",
                    "Accès": "",
                    "Mode": "", #add
                    "Rôle": "",
                    "Type": "",
                    "Membre": "",
                    "Tag": "",
                    "Commentaire": ""
                }
                in_secondary_block = False
                continue

            # Fin d'un bloc d'interface
            if current_interface and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_interface_data:
                    interfaces.append(current_interface_data)
                current_interface = None
                current_interface_data = None
                in_secondary_block = False
                continue

            # Traitement des paramètres de l'interface
            if current_interface and current_interface_data:
                # Début du bloc secondaryip
                if current_indentation == indentation_level + 8 and stripped_line == "config secondaryip":
                    in_secondary_block = True
                    continue

                # Fin du bloc secondaryip
                if in_secondary_block and current_indentation == indentation_level + 8 and stripped_line == "end":
                    in_secondary_block = False
                    continue

                # Extraction des IP secondaires
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

                # Paramètres standard de l'interface (non dans le bloc secondaryip)
                if not in_secondary_block and current_indentation == indentation_level + 8:
                    if stripped_line.startswith("set vdom "):
                        current_interface_data["Vdom"] = stripped_line[9:].strip().strip('"')
                    elif stripped_line.startswith("set ip "):
                        parts = stripped_line[7:].split()
                        if len(parts) >= 2:
                            current_interface_data["Adresse IP"] = parts[0]
                            current_interface_data["NetMask"] = parts[1]
                    elif stripped_line.startswith("set vlanid "):
                        current_interface_data["VLAN ID"] = stripped_line[11:].strip()
                        # Si un VLAN ID est défini, définir automatiquement le type sur "Vlan"
                        current_interface_data["Type"] = "Vlan"
                    elif stripped_line.startswith("set allowaccess "):
                        current_interface_data["Accès"] = stripped_line[15:].strip()
                    elif stripped_line.startswith("set mode"): #add
                        current_interface_data["Mode"] = stripped_line[9:].strip().strip('"') #add
                    elif stripped_line.startswith("set role "):
                        current_interface_data["Rôle"] = stripped_line[9:].strip()
                    elif stripped_line.startswith("set type ") and not current_interface_data["VLAN ID"]:
                        # Ne définir le type que s'il n'y a pas déjà un VLAN ID (qui aurait défini le type sur "Vlan")
                        current_interface_data["Type"] = stripped_line[9:].strip()
                    elif stripped_line.startswith("set member "):
                        # Extraire les membres sans les guillemets
                        members = re.findall(r'"([^"]+)"', stripped_line[11:])
                        if members:
                            current_interface_data["Membre"] = " ; ".join(members)
                        else:
                            current_interface_data["Membre"] = stripped_line[11:].strip()
                    elif stripped_line.startswith("set alias "):
                        current_interface_data["Commentaire"] = stripped_line[10:].strip().strip('"')
                    elif stripped_line.startswith("set interface "):
                        parent_interface = stripped_line[13:].strip().strip('"')
                        # Stocker temporairement l'interface parente pour associer le tag VLAN
                        current_interface_data["_parent_interface"] = parent_interface

        # Ajouter le dernier interface s'il n'a pas été ajouté
        if current_interface_data:
            interfaces.append(current_interface_data)

        # Associer les tags VLAN aux interfaces parentes
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

            # Nettoyer la propriété temporaire
            if "_parent_interface" in interface:
                del interface["_parent_interface"]

    return interfaces
