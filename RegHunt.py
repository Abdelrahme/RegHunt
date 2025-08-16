import os
import argparse
import json
import csv
import xml.etree.ElementTree as ET
import re

# Try to import winreg for live registry access (Windows only)
try:
    import winreg
    WINDOWS = True
except ImportError:
    WINDOWS = False

from Registry import Registry

def match_keyword(value, keyword, use_regex):
    try:
        value_str = str(value)
        if use_regex:
            return re.search(keyword, value_str, re.IGNORECASE) is not None
        else:
            return keyword.lower() in value_str.lower()
    except Exception:
        return False

# ---------------- Live Registry ----------------
def search_live_registry(root, root_name, keyword, results, use_regex):
    try:
        with winreg.OpenKey(root, "") as key:
            search_live_key(key, root_name, keyword, results, use_regex)
    except Exception:
        pass

def search_live_key(key, path, keyword, results, use_regex):
    try:
        for i in range(winreg.QueryInfoKey(key)[1]):
            name, value, _ = winreg.EnumValue(key, i)
            if match_keyword(value, keyword, use_regex):
                results.append({"path": path, "name": name, "value": str(value)})
    except Exception:
        pass
    try:
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)
            try:
                with winreg.OpenKey(key, subkey_name) as subkey:
                    search_live_key(subkey, f"{path}\\{subkey_name}", keyword, results, use_regex)
            except Exception:
                pass
    except Exception:
        pass

# ---------------- Hive Files ----------------
def search_hive_file(file_path, keyword, results, use_regex):
    try:
        reg = Registry.Registry(file_path)
        search_hive_key(reg.root(), keyword, results, use_regex)
    except Exception as e:
        results.append({"path": file_path, "error": str(e)})

def search_hive_key(key, keyword, results, use_regex):
    for value in key.values():
        try:
            if match_keyword(value.value(), keyword, use_regex):
                results.append({"path": key.path(), "name": value.name(), "value": str(value.value())})
        except Exception:
            pass
    for subkey in key.subkeys():
        search_hive_key(subkey, keyword, results, use_regex)

# ---------------- Save Results ----------------
def save_results(results, filename, fmt):
    if fmt.lower() == "json":
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
    elif fmt.lower() == "csv":
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "name", "value"])
            writer.writeheader()
            for item in results:
                if "path" in item:
                    writer.writerow(item)
    elif fmt.lower() == "xml":
        root_elem = ET.Element("RegistryResults")
        for item in results:
            entry = ET.SubElement(root_elem, "Entry")
            for key, val in item.items():
                child = ET.SubElement(entry, key)
                child.text = val
        tree = ET.ElementTree(root_elem)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
    else:
        # Default TXT fallback
        with open(filename, "w", encoding="utf-8") as f:
            for item in results:
                f.write(str(item) + "\n")

# ---------------- Main ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Keyword to search")
    parser.add_argument("-d", "--directory", help="Directory of hive files (optional)")
    parser.add_argument("--live", action="store_true", help="Search live registry (Windows only)")
    parser.add_argument("-f", "--format", default="txt", help="Output format: txt, csv, json, xml")
    parser.add_argument("-o", "--output", default="registry_results", help="Output file name (without extension)")
    parser.add_argument("--regex", action="store_true", help="Enable regex search")
    args = parser.parse_args()

    keyword = args.input
    use_regex = args.regex
    results = []

    if args.live:
        if not WINDOWS:
            print("[!] Live registry search is only supported on Windows. Skipping live search.")
            exit
        else:
            search_live_registry(winreg.HKEY_LOCAL_MACHINE, "HKLM", keyword, results, use_regex)
            search_live_registry(winreg.HKEY_CURRENT_USER, "HKCU", keyword, results, use_regex)
            search_live_registry(winreg.HKEY_USERS, "HKU", keyword, results, use_regex)

    if args.directory:
        hive_dir = args.directory
        if not os.path.isdir(hive_dir):
            print(f"[!] Directory not found: {hive_dir}")
        else:
            for filename in os.listdir(hive_dir):
                file_path = os.path.join(hive_dir, filename)
                if os.path.isfile(file_path):
                    # Match typical registry hive files
                    if filename.lower().endswith((".dat", ".hiv")) or filename.isupper():
                        search_hive_file(file_path, keyword, results, use_regex)

    if not args.live and not args.directory:
        print("[!] Must provide --live or --directory")
        return
    if results:

        output_file = f"{args.output}.{args.format}"
        save_results(results, output_file, args.format)
        print(f"[+] Results saved to {output_file}")
    else:
        print("[!] No results found. Nothing was saved.")

if __name__ == "__main__":
    main()
