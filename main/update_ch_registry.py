# Python3 script to update the Swiss plane in the registration database
# Needs Python 3.7 and aiohttp pypy package

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

async def post(session, url, d):
    async with session.post(url, json=d) as response:
        return await response.text()


async def get_plane(plane_id, sem):
    c2 = conn.cursor()
    c2.execute('SELECT * FROM plane_registrations WHERE registration=?', (plane_id,))
    if c2.fetchone() is not None:
        return

    c2 = conn.cursor()

    # Search for IT
    url = 'https://app02.bazl.admin.ch/web/bazl-backend/lfr'
    values = {"page_result_limit":10,"current_page_number":1,"sort_list":"registration",
            "totalItems":13334,"queryProperties":{"showDeregistered":False,"registration":plane_id},"query":{"showDeregistered":False,"registration":plane_id},"language":"en"}
    async with sem:
        async with aiohttp.ClientSession() as session:
            html = await post(session, url, values)

    plane_det = json.loads(html)
    for p in plane_det:
        if p['registration'] == plane_id:
            plane_det = p
            break

    if isinstance(plane_det, list):
        print("Error for (not found)", plane_id)
        return

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
        print("Error for (no good data)", plane_id)

async def main():
    url = 'https://app02.bazl.admin.ch/web/bazl-backend/lfr/ids'
    values = {"page_result_limit":10,"current_page_number":1,"sort_list":"registration",
            "totalItems":13334,"queryProperties":{"showDeregistered":False},"query":{"showDeregistered":False},"language":"en"}

    data = json.dumps(values).encode() # data should be bytes
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
                'Referer': 'https://app02.bazl.admin.ch/web/bazl/fr/#/lfr/search',
                'Content-Type': 'application/json;charset=UTF-8'}
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()

    ids=json.loads(the_page)


    # Max 200 concurrent requests
    sem = asyncio.Semaphore(200)
    tasks = [get_plane(i, sem) for i in ids]
    await asyncio.wait(tasks)

if __name__ == "__main__":   
    try:
        asyncio.run(main())
    finally:
        conn.commit()
        conn.close()
