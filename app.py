from flask import Flask, render_template, request
import requests
import socket
import ssl
import subprocess
import time

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        nmap_scan = 'nmap' in request.form


        url_cleaned = url.replace('http://', '').replace('https://', '')


        try:
            start_time = time.time()
            response = requests.get(url)
            load_time = time.time() - start_time
        except requests.exceptions.RequestException as e:
            load_time = f"Ошибка: {e}"


        try:
            dns_info = socket.gethostbyname_ex(url_cleaned)
            dns_info_formatted = f"Основное имя хоста: {dns_info[0]}\n" \
                                 f"Алиасы: {', '.join(dns_info[1])}\n" \
                                 f"IP-адреса: {', '.join(dns_info[2])}"
        except socket.error:
            dns_info_formatted = "DNS-запись не найдена"


        try:
            cert_info = ssl.get_server_certificate((url_cleaned, 443))
        except ssl.SSLError:
            cert_info = "SSL сертификат не найден или ошибка"


        if nmap_scan:
            try:
                nmap_result = subprocess.getoutput(f"nmap {url_cleaned}")
            except Exception as e:
                nmap_result = f"Ошибка при Nmap-сканировании: {e}"
        else:
            nmap_result = "Nmap-сканирование не выполнялось."


        return render_template('result.html', load_time=load_time, ip_address=dns_info[2][0],
                               cert_info=cert_info, nmap_result=nmap_result, dns_info=dns_info_formatted)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
