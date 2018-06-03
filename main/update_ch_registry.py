# Python3 script to update the Swiss plane in the registration database

import asyncio
import json
import aiohttp
import urllib.parse
import urllib.request
import sqlite3
conn = sqlite3.connect('plane_regs.sqlite3')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS plane_registrations
             (registration text, transponder unsigned big int, manufacturer text, model text, icaoModel text)''')
c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_transponder ON plane_registrations (transponder)''')
c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_reg ON plane_registrations (registration)''')

c.execute("SELECT COUNT(registration) FROM plane_registrations")

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

# Max 200 concurrent requests
sem = asyncio.Semaphore(200)

async def get_plane(plane_id):
    c2 = conn.cursor()
    c2.execute('SELECT * FROM plane_registrations WHERE registration=?', (plane_id,))
    if c2.fetchone() is not None:
        return

    c2 = conn.cursor()
    url = 'https://www.bazlwork.admin.ch/bazl-backend/lfr/{}'.format(plane_id)
    async with sem:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, url)

    plane_det = json.loads(html)
    if 'details' in plane_det and 'aircraftAddresses' in plane_det['details']:
            transponder = plane_det['details']['aircraftAddresses']['hex'].lower()
            if transponder != 'n/a':
                trans_numb = int("0x"+transponder, 0)
                ret = c2.execute('INSERT INTO plane_registrations VALUES (?,?,?,?,?)', (plane_id,trans_numb, plane_det['manufacturer'], plane_det['aircraftModelType'], plane_det['icaoCode']))
                print("{}: {}".format(trans_numb, plane_id))
                c2 = conn.cursor()
                c2.execute('SELECT * FROM plane_registrations WHERE registration=?', (plane_id,))
                assert(c2.fetchone() is not None)
                

    else:
        print("Error for ", plane_id)

if __name__ == "__main__":   
    url = 'https://www.bazlwork.admin.ch/bazl-backend/lfr/ids'
    values = {"page_result_limit":10,"current_page_number":1,"sort_list":"registration",
            "totalItems":3334,"query":{},"language":"en","tab":"basic"}

    data = json.dumps(values).encode() # data should be bytes
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
                'Referer': 'https://www.bazlwork.admin.ch/bazl/',
                'Content-Type': 'application/json;charset=UTF-8'}
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()

    ids=json.loads(the_page)
    try:
        loop = asyncio.get_event_loop()
        tasks = [asyncio.async(get_plane(i)) for i in ids]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
    finally:
        conn.commit()
        conn.close()
