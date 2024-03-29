import os
import requests
import threading

# Definir un Lock para sincronizar el acceso a variables compartidas
lock = threading.Lock()

def main():
    # Limpiar la pantalla
    limpiar_pantalla()

    # Eliminar archivos si existen
    eliminar_archivos(['buenos.txt', 'errores.txt', 'prohibidos.txt'])

    archivo_proxies = 'proxies.txt'
    cantidad_por_lote = 10

    niantic_url = 'https://pgorelease.nianticlabs.com/plfe/version'
    #ptc_url = 'https://sso.pokemon.com/sso/login?locale=en&service=https://www.pokemon.com/us/pokemon-trainer-club/caslogin'
    ptc_url = 'https://access.pokemon.com/oauth2/auth?scope=openid+offline+email'

    niantic_headers = {'User-Agent': 'Niantic App'}
    ptc_headers = {'User-Agent': 'pokemongo/1 CFNetwork/811.4.18 Darwin/16.5.0', 'Host': 'sso.pokemon.com'}

    proxies = leer_proxies(archivo_proxies)
    print('Se van a probar {} proxies.'.format(len(proxies)))

    # Usar listas compartidas para contar buenos, prohibidos y errores
    buenos = [0]
    prohibidos = [0]
    errores = [0]

    for i in range(0, len(proxies), cantidad_por_lote):
        lote_proxies = proxies[i:i+cantidad_por_lote]
        threads = []
        for p in lote_proxies:
            thread = threading.Thread(target=verificar_proxy, args=(p, niantic_url, ptc_url, niantic_headers, ptc_headers, buenos, prohibidos, errores))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    print('Comprobación de proxies finalizada.')
    print('Resumen:')
    print('- Total de proxies probados:', len(proxies))
    print('- Proxies buenos:', buenos[0])
    print('- Proxies prohibidos:', prohibidos[0])
    print('- Proxies con errores:', errores[0])

def limpiar_pantalla():
    # Limpiar la pantalla en función del sistema operativo
    os.system('cls' if os.name == 'nt' else 'clear')

def eliminar_archivos(archivos):
    for archivo in archivos:
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f'{archivo} eliminado.')

def leer_proxies(archivo_proxies):
    with open(archivo_proxies, 'r') as f:
        proxies = f.read().splitlines()
    return proxies

def verificar_proxy(proxy, niantic_url, ptc_url, niantic_headers, ptc_headers, buenos, prohibidos, errores):
    pr = {'http': proxy, 'https': proxy}
    
    print('Probando proxy {}...'.format(proxy))
    
    try:
        resultado_niantic = comprobar_proxy_para_servicio(proxy, niantic_url, niantic_headers, 'Niantic', 10)
        print('Probando Niantic... proxy {} Estado {}'.format(proxy, resultado_niantic))
        
        resultado_ptc = comprobar_proxy_para_servicio(proxy, ptc_url, ptc_headers, 'PTC', 10)
        print('Probando PTC... proxy {} Estado {}'.format(proxy, resultado_ptc))
        
        # Usar el Lock para sincronizar el acceso a variables compartidas
        with lock:
            if '200 OK, el proxy no está prohibido.' in resultado_niantic and '200 OK, el proxy no está prohibido.' in resultado_ptc:
                escribir_archivo(proxy, 'buenos.txt')
                buenos[0] += 1
            elif '403 Error, el proxy está prohibido.' in resultado_niantic or '403 Error, el proxy está prohibido.' in resultado_ptc:
                escribir_archivo(proxy, 'prohibidos.txt')
                prohibidos[0] += 1
            else:
                escribir_archivo(proxy, 'errores.txt')
                errores[0] += 1
    except Exception as e:
        #print('Error al verificar el proxy {}: {}'.format(proxy, e))
        print('Error al verificar el proxy {}: '.format(proxy))
        escribir_archivo(proxy, 'errores.txt')
        # Usar el Lock para sincronizar el acceso a variables compartidas
        with lock:
            errores[0] += 1

def comprobar_proxy_para_servicio(proxy, url, headers, nombre_servicio, timeout):
    r = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=float(timeout), headers=headers)
    if r.status_code == 200:
        return '200 OK, el proxy no está prohibido.'
    elif r.status_code in [403, 409]:
        return '{} Error, el proxy está prohibido.'.format(r.status_code)
    else:
        return '{} Error.'.format(r.status_code)

def escribir_archivo(proxy, archivo):
    # Asegurarse de que el archivo exista antes de intentar escribir en él
    if not os.path.exists(archivo):
        open(archivo, 'w').close()  # Crear el archivo si no existe
    
    with open(archivo, 'a') as f:
        f.write(proxy + '\n')
        print(f'{proxy} escrito en {archivo} con éxito.')

if __name__ == '__main__':
    main()
