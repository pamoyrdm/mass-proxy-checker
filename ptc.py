import requests

def verificar_proxy(proxy_url):
    try:
        response = requests.get("https://www.example.com", proxies={"http": proxy_url, "https": proxy_url}, timeout=10)
        if response.status_code == 200:
            print("El proxy {} está disponible.".format(proxy_url))
        else:
            print("El proxy {} está disponible pero devolvió un código de estado diferente de 200: {}".format(proxy_url, response.status_code))
    except requests.RequestException as e:
        print("Error al conectar al proxy {}: {}".format(proxy_url, e))

# Ejemplo de proxy
proxy_url = "http://ewuftmya:8jzuhx0wvkxy@45.196.32.130"

# Verificar el proxy
verificar_proxy(proxy_url)
