
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
