import os

import requests
import json
import dateutil.parser
import re
import mysql.connector as mariadb

offset = '2017-08-13'
tenders_subdir = 'tenders'

r = requests.get('http://public.api.openprocurement.org/api/2.3/tenders?offset={0}'.format(offset))

if r.status_code == 200:
    tenders_list = r.json()
    print("Tenders list got for offset {0}. Tenders count: {1}\n{2}".format(offset, len(tenders_list['data']), tenders_list['data'][0] if len(tenders_list['data'])>0 else ''))

else:
    print('Failed to get tenders list for offset {0}. Code: {1}'.format(offset, r.status_code))
    exit(-1)

if not os.path.exists(tenders_subdir):
    os.makedirs(tenders_subdir)

conn = mariadb.connect(host='127.0.0.1', user='root', password='root', database='reports_data')
print(conn)

regex1 = re.compile(r'\\"', re.IGNORECASE)
regex2 = re.compile(r'"\+\\u0.+?"', re.IGNORECASE)
regex3 = re.compile(r'"\\u0.+?"', re.IGNORECASE)
regex4 = re.compile(r'\\u0[\\u0-9a-zA-Z]*\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)
regex5 = re.compile(r'\\u0[0-9a-zA-Z]{3}', re.IGNORECASE)

for t in tenders_list['data']:
    dtm = dateutil.parser.parse(t['dateModified'])
    id = t['id']
    subdir = '{0}/{1:04d}-{2:02d}-{3:02d}'.format(tenders_subdir, dtm.year, dtm.month, dtm.day)
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    file_path = "{0}/{1}.json".format(subdir, id)
    pretty_file_path = "{0}/{1}_pretty.json".format(subdir, id)

    if not os.path.exists(file_path) or not os.path.exists(pretty_file_path):
        r = requests.get('http://public.api.openprocurement.org/api/2.3/tenders/{0}'.format(id))

        if r.status_code == 200:
            response_json = r.json()

            with open(file_path, "w") as text_file:
                json.dump(response_json, text_file, separators=(',', ':'))

            with open(pretty_file_path, "w") as text_file:
                json.dump(response_json, text_file, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            print('Failed to get tender {0}! Error: {1} {2}'.format(id, r.status_code, r.text))
    else:
        print('Tender {0} already got.'.format(id))

        with open(file_path, "r") as text_file:
            response_json = json.load(text_file)

    tender_data = response_json['data']

    if 'enquiryPeriod' in tender_data:

        cursor = conn.cursor(buffered=False)
        str = json.dumps(response_json, separators=(',', ':'))

        strcut = regex1.sub('', str)
        strcut = regex2.sub('""', strcut)
        strcut = regex3.sub('""', strcut)
        strcut = regex4.sub('', strcut)
        strcut = regex5.sub('', strcut)

        res = cursor.callproc('sp_update_tender',
                              (strcut, t['dateModified'], 0, ''))
        if res[2] != 0:
            print(str)
            print(strcut)
            print('!!!!  sp_update_tender result for {0}: {1}; {2}'.format(id, res[2], res[3]))

        if "bids" in tender_data:
            # print("Tender {0} got. Bids count: {1}".format(id, len(tender_data['bids'])))

            if len(tender_data['bids']) > 0:
                for b in tender_data['bids']:
                    if 'tenderers' in b:
                        for tendr in b['tenderers']:
                            # print(u'Got tenderer: {0} {1} {2}'.format(tendr['identifier']['id'], tendr['identifier']['scheme'], tendr['identifier']['legalName']))
                            # .decode("utf-8")
                            pass
        else:
            print("Tender {0} got without bids. Status: {1}".format(id, tender_data['status']))

    else:
        print("Tender {0} has no enquiry period! Status: {1}".format(id, tender_data['status']))
