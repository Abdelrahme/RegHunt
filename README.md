# Registry Search Tool

A Python tool for searching Windows Registry hives (live system or offline files) for specific keywords or regex patterns. Useful for incident response, forensic analysis, and threat hunting.

---

## Features

- **Live Registry Scanning (Windows only)**: Enumerates all keys/values in HKEY\_LOCAL\_MACHINE, HKEY\_CURRENT\_USER, HKEY\_USERS.
- **Offline Hive Analysis**: Recursively scans directories for registry hive files (`.dat`, `.hiv`, or uppercase names) and searches them.
- **Flexible Search**: Supports substring search or regex patterns.
- **Output Formats**: TXT, CSV, JSON, XML.
- **Case-Insensitive Search**: Matches regardless of case.
- **Error Handling**: Reports inaccessible keys or corrupt hive files.

---

## Prerequisites

- Python 3
- Windows (for live registry access) or Linux/macOS (offline hive scanning supported)
- `python-registry` module for offline hive parsing:
 ```bash
pip install python-registry
```

---



## Usage

```bash
python3 main.py -i <keyword> [options]
```

### Options

| Option              | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `-i`, `--input`     | Keyword to search (required)                                    |
| `-d`, `--directory` | Directory containing hive files (optional)                      |
| `--live`            | Search live registry (Windows only)                             |
| `-f`, `--format`    | Output format: txt, csv, json, xml (default: txt)               |
| `-o`, `--output`    | Output file name without extension (default: registry\_results) |
| `--regex`           | Enable regex search                                             |

### Examples

Search live registry for `notepad.exe` (Windows only):

```bash
python3 main.py -i notepad.exe --live -f csv -o results
```

Search offline hive directory with regex for IP addresses:

```bash
python3 main.py -i "\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b" -d ./hives --regex -f json -o ip_results
```

---

## Output

For each match, the tool outputs:

- **Path**: Registry key path or hive file
- **Name**: Value name
- **Value**: Value data

Saved to the specified format (`.txt`, `.csv`, `.json`, `.xml`).

If no results are found, nothing is saved.

---

## Build / Compilation (Optional)

To create a standalone executable (Windows recommended):

```bash
pyinstaller --onefile main.py
```

This produces `dist/main.exe` on Windows or `dist/main` on Linux/macOS.

---

## Security Considerations

- Hive files may contain sensitive information.
- When scanning live registries, ensure appropriate permissions and legal authorization.

---

## License

Provided for educational, forensic, and research purposes. Use responsibly.

