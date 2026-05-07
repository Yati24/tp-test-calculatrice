import threading
import time
import socket

from app import app, init_db

from playwright.sync_api import sync_playwright


def run_server():
    init_db()
    app.run(port=5001)


def wait_port(host, port, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            s = socket.create_connection((host, port), timeout=0.5)
            s.close()
            return True
        except Exception:
            time.sleep(0.1)
    return False


def test_e2e_calculation():
    server = threading.Thread(target=run_server, daemon=True)
    server.start()
    assert wait_port('127.0.0.1', 5001, timeout=5)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://127.0.0.1:5001')
        page.fill('#a', '7')
        page.fill('#b', '6')
        page.select_option('#op', '+')
        page.click('button:has-text("Calculer")')
        page.wait_for_function('document.querySelector(".result-val") && document.querySelector(".result-val").innerText.trim() !== "—"', timeout=3000)
        text = page.inner_text('#result')
        assert '13' in text
        page.wait_for_selector('#history-list li')
        page.click('#history-list li')
        a_val = page.input_value('#a')
        b_val = page.input_value('#b')
        op_val = page.input_value('#op')
        assert a_val == '7'
        assert b_val == '6'
        assert op_val == '+'
        browser.close()
