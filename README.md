# Selenium Proxy Authentication Diagnostic

A small Selenium 4 + Chrome diagnostic example for checking a proxy route and a target website in separate stages.

## Scope and limitations

- Uses proxy IP allowlisting.
- Configures the HTTP proxy endpoint for both HTTP and HTTPS destinations.
- Does **not** implement HTTP proxy username/password authentication.
- Does not guarantee that a destination website will allow the request.
- A Selenium timeout or WebDriver exception is not proof of an HTTP 407 response.

## Requirements

- Python 3.9+
- Google Chrome installed
- A Selenium-compatible ChromeDriver setup. Recent Selenium versions may manage the driver automatically when the environment allows it.
- A proxy endpoint that supports HTTP proxy connections and has authorized the public egress IP of the machine running Chrome.

## Install

```bash
python -m venv .venv
```

Activate the virtual environment, then:

```bash
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` or export the variables in your shell. The script does not automatically load `.env`, so export the values or use your preferred environment-variable loader.

Required:

- `PROXY_SERVER`: proxy hostname and port, for example `gateway.example.com:12345`
- `TARGET_URL`: a site you own or are authorized to test

Optional:

- `IP_CHECK_URL`: defaults to `https://api.ipify.org?format=json`
- `PAGE_LOAD_TIMEOUT`: defaults to 45 seconds
- `ELEMENT_WAIT_TIMEOUT`: defaults to 15 seconds

Do not put credentials in the repository or commit real proxy credentials.

## Run

Linux / macOS:

```bash
export PROXY_SERVER="your-proxy-host:port"
export TARGET_URL="https://example.com/"
python selenium_proxy_diagnostic.py
```

PowerShell:

```powershell
$env:PROXY_SERVER = "your-proxy-host:port"
$env:TARGET_URL = "https://example.com/"
python .\selenium_proxy_diagnostic.py
```

## How to interpret the result

1. **WebDriver startup** fails: investigate Chrome, ChromeDriver, Selenium, and the local browser environment first.
2. **Proxy route / IP-check** fails: investigate proxy host, port, protocol, allowlist, network access, and the IP-check destination.
3. **Target website access** fails: the proxy route may be working; investigate target-site response, page behavior, and wait conditions.

The script reports the exception type and failing stage. Confirm an HTTP `407 Proxy Authentication Required` from an actual proxy response or provider logs before diagnosing it as a 407.

## Remote WebDriver / Selenium Grid

The browser node makes the proxy connection. Ensure that node can reach the proxy endpoint and, when using IP allowlisting, authorize the node's public egress IP. The Python client machine's IP may be different.
