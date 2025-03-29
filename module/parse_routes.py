def parse_routes(input_file):
    routes = []

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        route_config_started = False
        current_route = None
        indentation_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Determine indentation level by counting spaces at the beginning of the line
            if line.startswith(' '):
                current_indentation = len(line) - len(line.lstrip())
            else:
                current_indentation = 0

            # Start of route configuration block (first level)
            if current_indentation == 0 and stripped_line == "config router static":
                route_config_started = True
                indentation_level = current_indentation
                continue

            # End of route configuration block (first level)
            if route_config_started and current_indentation == indentation_level and stripped_line == "end":
                route_config_started = False
                continue

            if not route_config_started:
                continue

            # Processing lines in route configuration block
            if current_indentation == indentation_level + 4 and stripped_line.startswith("edit "):
                # Beginning of a new route block
                if current_route:
                    routes.append(current_route)

                current_route = {
                    "Destination": "",
                    "Interface": "",
                    "Gateway": "",
                    "Priorité": "",
                    "Distance Administrative": "",
                    "Blackhole": "disable",
                    "Commentaire": ""
                }
                continue

            # End of a route block
            if current_route and current_indentation == indentation_level + 4 and stripped_line == "next":
                if current_route:
                    routes.append(current_route)
                current_route = None
                continue

            # Processing route parameters
            if current_route and current_indentation == indentation_level + 8:
                if stripped_line.startswith("set dst "):
                    current_route["Destination"] = stripped_line[8:].strip()
                elif stripped_line.startswith("set device "):
                    current_route["Interface"] = stripped_line[11:].strip().strip('"')
                elif stripped_line.startswith("set gateway "):
                    current_route["Gateway"] = stripped_line[12:].strip()
                elif stripped_line.startswith("set priority "):
                    current_route["Priorité"] = stripped_line[13:].strip()
                elif stripped_line.startswith("set distance "):
                    current_route["Distance Administrative"] = stripped_line[13:].strip()
                elif stripped_line.startswith("set blackhole "):
                    current_route["Blackhole"] = stripped_line[13:].strip()
                elif stripped_line.startswith("set comment "):
                    current_route["Commentaire"] = stripped_line[12:].strip().strip('"')

        # Add the last route if it hasn't been added
        if current_route:
            routes.append(current_route)

    return routes