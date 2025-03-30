
def parse_users(input_file):
    users = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        user_config_started = False
        current_user = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of user configuration block (first level)
            if current_indentation == 0 and stripped_line == "config user local":
                user_config_started = True
                indentation_level = current_indentation
                continue

            # End of user configuration block (first level)
            if user_config_started and current_indentation == indentation_level and stripped_line == "end":
                user_config_started = False
                continue

            if not user_config_started:
                continue

            # Processing lines in user configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new user block
                if current_user:
                    users.append(current_user)

                user_name = stripped_line[5:].strip().strip('"')
                current_user = {
                    "User": user_name,
                    "Type": "",
                    "MFA": "",
                    "Mail": ""
                }
                continue

            # End of a user block
            if current_user and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_user:
                    users.append(current_user)
                current_user = None
                continue

            # Processing user parameters
            if current_user and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set type "):
                    current_user["Type"] = stripped_line[9:].strip()
                elif stripped_line.startswith("set two-factor "):
                    current_user["MFA"] = stripped_line[14:].strip()
                elif stripped_line.startswith("set email-to "):
                    current_user["Mail"] = stripped_line[13:].strip().strip('"')

        # Add the last user if it hasn't been added
        if current_user:
            users.append(current_user)

    return users


def parse_admins(input_file):
    admins = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        admin_config_started = False
        current_admin = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Déterminer le niveau d'indentation en comptant les espaces au début de la ligne
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Début du bloc de configuration des administrateurs (premier niveau)
            if current_indentation == 0 and stripped_line == "config system admin":
                admin_config_started = True
                indentation_level = current_indentation
                continue

            # Fin du bloc de configuration des administrateurs (premier niveau)
            if admin_config_started and current_indentation == indentation_level and stripped_line == "end":
                admin_config_started = False
                continue

            if not admin_config_started:
                continue

            # Traitement des lignes dans le bloc de configuration des administrateurs
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Début d'un nouveau bloc d'admin
                if current_admin:
                    admins.append(current_admin)

                admin_name = stripped_line[5:].strip().strip('"')
                current_admin = {
                    "Name": admin_name,
                    "Profil Type": "",
                    "Vdom": "",
                    "Trust Host IPv4": "",
                    "Trust Host IPv6": ""
                }
                continue

            # Fin d'un bloc d'admin
            if current_admin and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_admin:
                    admins.append(current_admin)
                current_admin = None
                continue

            # Traitement des paramètres de l'admin
            if current_admin and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set accprofile "):
                    current_admin["Profil Type"] = stripped_line[15:].strip().strip('"')
                elif stripped_line.startswith("set vdom "):
                    current_admin["Vdom"] = stripped_line[9:].strip().strip('"')
                elif stripped_line.startswith("set trusthost"):
                    parts = stripped_line.split()
                    if len(parts) > 3:
                        ip_address = parts[2].strip()
                        subnet_mask = parts[3].strip()
                        trust_host = f"{ip_address} {subnet_mask}"
                        if current_admin["Trust Host IPv4"]:
                            current_admin["Trust Host IPv4"] += f"; {trust_host}"
                        else:
                            current_admin["Trust Host IPv4"] = trust_host
                elif stripped_line.startswith("set ip6-trusthost"):
                    parts = stripped_line.split()
                    if len(parts) > 2:
                        ipv6_address = parts[2].strip()
                        if current_admin["Trust Host IPv6"]:
                            current_admin["Trust Host IPv6"] += f"; {ipv6_address}"
                        else:
                            current_admin["Trust Host IPv6"] = ipv6_address

    return admins