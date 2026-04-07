# Meta Business Suite API Tool

Python requests-based client for the Meta Business Suite mobile API.

## Setup

```bash
pip install -r requirements.txt
```

## Input Files

**check.txt** — one account per line:
```
phone|password|2fa_secret
```

**proxies.txt** — one proxy per line (optional):
```
http://user:pass@host:port
socks5://host:port
```

## Usage

```bash
python main.py --accounts check.txt
python main.py --accounts check.txt --proxies proxies.txt
```

## Output

Results are saved to `results.txt` with format:
```
phone|status|details
```
