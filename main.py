from datetime import date

from pyscript import document, window
from pyodide.ffi import create_proxy

get = document.getElementById
proxies = []   


def listen(element, event, function):
    proxy = create_proxy(function)
    proxies.append(proxy)
    element.addEventListener(event, proxy)


get("yr").textContent = str(date.today().year)


def toggle_menu(event):
    get("menu").classList.toggle("open")


listen(get("burger"), "click", toggle_menu)
