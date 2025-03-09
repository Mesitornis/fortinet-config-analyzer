import re

def parse_system_info(input_file):
    hostname = ""
    model = ""
    version = ""
    build = ""
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        in_global_block = False
        for line in f:
            line = line.strip()
            
            # Extraction des informations de version
            if line.startswith("#config-version="):
                parts = line.split('=')[1].split('-')
                if len(parts) >= 3:
                    model = parts[0]
                    version = parts[1]
                    # Extraction du build entre "-FW-" et le prochain "-"
                    match = re.search(r'-FW-(.+?)-', line)
                    if match:
                        build = match.group(1)
            
            # Détection du bloc global
            if line == "config system global":
                in_global_block = True
                continue
            elif in_global_block and line == "end":
                in_global_block = False
                continue
            
            # Extraction du hostname dans le bloc global
            if in_global_block and line.startswith("set hostname"):
                hostname = line.split("set hostname")[1].strip().strip('"')
    
    return {
        "Hostname": hostname,
        "Modèle": model,
        "Version": version,
        "Build": build
    }
