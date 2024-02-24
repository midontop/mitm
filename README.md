# MiUU Server
## Instructions
You'll need python 3.9+

1. Install python and download / clone this repo
2. Run in a terminal pip install requests python-dotenv flask pyopenssl
3. Run the certs generator using python gen.py in the folder containing the code
4. Modify your C:\Windows\System32\drivers\etc\hosts file with the following content: 127.0.0.1 www.miubackend.net
5. Run python app.py in the folder containing the code
6. Open a chromium-based browser (e.g. chrome) and open "https://www.miubackend.net"
7. Ignore the security issue and download the certificate, then trust it (follow this guide https://www.pico.net/kb/how-do-you-get-chrome-to-accept-a-self-signed-certificate/)
8. Open https://www.miubackend.net/config to configure your custom server
9. With the server running, open marble it up! Ultra


## Removing
Remove the line from your hosts file :)
