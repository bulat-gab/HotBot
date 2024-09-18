# HOT tasks claimer

This program can 'watch' video tasks and submit codewords for you.

# Requirements

- Python 3.9+ (Tested on Python v3.12)
- Python added to PATH
- Required Python packages listed in requirements.txt.
- Google Chrome v128 and Chrome Driver installed (run `./scripts/install.sh` to install it )

# Installation

## Windows

Todo
...

## Linux

```
bash ./scripts/install.sh
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python3 ./main.py <ARGUMENTS>
```

## Optional

### Fix certificate issue with Selenium Wire Chrome Driver

#### Windows

`python -m seleniumwire extractcert`  
`certutil -addstore -f "Root" ./ca.crt`

#### Linux

`sudo apt install libnss3-tools`  
`python3 -m seleniumwire extractcert`  
`certutil -d sql:$HOME/.pki/nssdb -A -t TC -n "Selenium Wire" -i ./ca.crt`

### WebRTC

When using a proxy, your real IP address may be exposed through WebRTC. To prevent this in Google Chrome, you must use an extension that disables WebRTC.

For example, [WebRTC Network Limiter extension](https://chromewebstore.google.com/detail/webrtc-network-limiter/npeicpdbkakmehahjeeohfdhnlpdklia)

The extension's configuration must be set to 'disable_non_proxied_udp', other options will not prevent the IP leak.

#### How to configure

- Create `.env` file
- Set `DISABLE_WEBRTC = True`
- Download an extension and enter the path to it in `WEBRTC_EXTENSION_PATH =`. It should be a path to an unpacked extension (not to `.crx` file)  
  Example: `WEBRTC_EXTENSION_PATH = "./files/WebRTC_Network_Limiter_0.2.1.4_0"`

# 2. How to Run

`python3 ./main.py [-h] {tasks,ui} `

Available commands:

- `python3 ./main.py tasks` - begin solving video tasks for sessions from `./sessions` directory. Sessions must already be logged in.

- `python3 ./main.py tasks --with-login` - perform login first, then solve tasks for accounts listed in the `accounts.txt` file. Check `account.txt.example` for the correct format.

- `python3 ./main.py ui` - launch a browser with user interface. Provide a session name. If session does not exist, a new one will be created

- (Optional) `cp .env-example .env`  
   Edit `.env` For configuring different settings

# Troubleshooting

- Ensure that all required dependencies are installed.
- Execution may occasionally fail due to timeouts, stale elements, or network issues. Please try running the command again.

# Licence

This project is licensed under the GNU General Public License. See the [LICENSE](./LICENSE) file for details.
