import json
import re
import asyncio

from pyscript import document, window
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch


FORM_ENDPOINT = ""

get = document.getElementById
proxies = []   


def listen(element, event, function):
    proxy = create_proxy(function)
    proxies.append(proxy)
    element.addEventListener(event, proxy)


form = get("form")

if form:
    service = get("service")
    estimate = get("est")
    status = get("status")

    def show_price(event=None):
        if service.value == "":
            estimate.value = "Select a service"
            return
        option = service.options.item(service.selectedIndex)
        price = int(option.getAttribute("data-price"))
        estimate.value = "₱" + str(price) + " (listed price, final quotation to be confirmed)"

    listen(service, "change", show_price)

    wanted = window.URLSearchParams.new(window.location.search).get("service")
    if wanted:
        service.value = wanted
        show_price()

    def show_error(key, message):
        document.querySelector('[data-for="' + key + '"]').textContent = message
        box = get(key)
        if box:
            if message:
                box.classList.add("bad")
            else:
                box.classList.remove("bad")

    def check_form():
        ok = True

        name = get("name").value.strip()
        if len(name) < 2:
            show_error("name", "Please enter your full name.")
            ok = False
        else:
            show_error("name", "")

        email = get("email").value.strip()
        if email == "":
            show_error("email", "Please enter your email address.")
            ok = False
        elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", email):
            show_error("email", "Enter a valid email address, like name@example.com.")
            ok = False
        else:
            show_error("email", "")

        phone = get("phone").value.strip()
        if phone == "":
            show_error("phone", "Please enter your contact number.")
            ok = False
        elif not re.match(r"^[+()\d\s-]{7,}$", phone):
            show_error("phone", "Enter a valid contact number (numbers only).")
            ok = False
        else:
            show_error("phone", "")

        if get("ctype").value == "":
            show_error("ctype", "Please select your customer type.")
            ok = False
        else:
            show_error("ctype", "")

        if get("comp").value == "":
            show_error("comp", "Please select Desktop or Laptop.")
            ok = False
        else:
            show_error("comp", "")

        if service.value == "":
            show_error("service", "Please select the service you need.")
            ok = False
        else:
            show_error("service", "")

        if len(get("desc").value.strip()) < 10:
            show_error("desc", "Please describe the problem (at least 10 characters).")
            ok = False
        else:
            show_error("desc", "")

        if document.querySelector("[name=contact_method]:checked") is None:
            show_error("method", "Please choose Email or Phone.")
            ok = False
        else:
            show_error("method", "")

        if not get("consent").checked:
            show_error("consent", "Please agree to be contacted.")
            ok = False
        else:
            show_error("consent", "")

        return ok

    async def send_request(data):
        button = get("submit")
        button.disabled = True
        button.textContent = "Sending..."
        try:
            response = await pyfetch(
                FORM_ENDPOINT,
                method="POST",
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                body=json.dumps(data),
            )
            if response.ok:
                form.reset()
                show_price()
                status.className = "ok"
                status.textContent = "Thank you! Your service request was sent. We will contact you about the diagnosis and quotation. This is not a repair approval."
            else:
                status.className = "fail"
                status.textContent = "Your request could not be sent. Please try again."
        except Exception:
            status.className = "fail"
            status.textContent = "Your request could not be sent. Please check your internet and try again."
        button.disabled = False
        button.textContent = "Submit Service Request"

    def submit_form(event):
        event.preventDefault()   
        status.className = ""
        status.textContent = ""

        if not check_form():
            status.className = "fail"
            status.textContent = "Please fix the errors above and submit again."
            return

        if FORM_ENDPOINT == "":
            status.className = "demo"
            status.textContent = "Demo mode: this form is not connected to an email service yet, so your request was NOT sent."
            return

        data = {
            "name": get("name").value,
            "email": get("email").value,
            "phone": get("phone").value,
            "customer_type": get("ctype").value,
            "computer_type": get("comp").value,
            "service": service.value,
            "estimated_price": estimate.value,
            "problem": get("desc").value,
            "contact_method": document.querySelector("[name=contact_method]:checked").value,
            "consent": True,
        }
        asyncio.ensure_future(send_request(data))

    listen(form, "submit", submit_form)
