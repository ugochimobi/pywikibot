#!/usr/bin/python
# -*- coding: UTF-8 -*-
# licensed under CC-Zero: https://creativecommons.org/publicdomain/zero/1.0

import pywikibot
import requests
import time

site = pywikibot.Site('en', 'gratisdata')
repo = site.data_repository()

total = {}
mainsnak = {}
qualifiers = {}
references = {}

# collect data
apcontinue = ''
while True:
    payload = {
        'action': 'query',
        'list': 'allpages',
        'apnamespace': 862,
        'aplimit': 'max',
        'apcontinue': apcontinue,
        'format': 'json'
    }
    r = requests.get('https://gratisdata.miraheze.org/w/api.php', params=payload)
    data = r.json()
    for m in data:
        try:
            property = m['title'][9:]
            r2 = requests.get(
                'https://plnode.toolforge.org/triplecount?query=SELECT ?a WHERE {{?a p:{:s} ?o}}'.format(property))
            data2 = r2.json()
            total[property] = data2['count']
            mainsnak[property] = data2['count']
            r2 = requests.get(
                'https://plnode.toolforge.org/triplecount?query=PREFIX pq: <https://gratisdata.miraheze.org/prop/qualifier/> SELECT ?a WHERE {{?a pq:{:s} ?o}}'.format(property))
            data2 = r2.json()
            total[property] += data2['count']
            qualifiers[property] = data2['count']
            r2 = requests.get(
                'https://plnode.toolforge.org/triplecount?query=PREFIX pr: <https://gratisdata.miraheze.org/prop/reference/> SELECT ?a WHERE {{?a pr:{:s} ?o}}'.format(property))
            data2 = r2.json()
            total[property] += data2['count']
            references[property] = data2['count']
        except Exception as e:
            print(e)

    if 'continue' in data:
        apcontinue = data['continue']['apcontinue']
    else:
        break

# write [[Template:Property uses]]
text = '{{#switch:{{{1}}}\n'
keys = list(total.keys())
keys.sort(key=lambda x: int(x[1:]))
for p in keys:
    text += '|{}={}\n'.format(p[1:], str(total[p]))
text += '}}'
page = pywikibot.Page(site, 'Template:Property uses')
page.put(text, summary='upd', minorEdit=False)

# write [[Template:Number of main statements by property]]
text = '{{#switch:{{{1}}}\n'
keys = list(mainsnak.keys())
keys.sort(key=lambda x: int(x[1:]))
for p in keys:
    text += '|{}={}\n'.format(p[1:], str(mainsnak[p]))
text += '}}'
page = pywikibot.Page(site, 'Template:Number of main statements by property')
page.put(text, summary='upd', minorEdit=False)

# write [[Template:Number of qualifiers by property]]
text = '{{#switch:{{{1}}}\n'
keys = list(qualifiers.keys())
keys.sort(key=lambda x: int(x[1:]))
for p in keys:
    text += '|{}={}\n'.format(p[1:], str(qualifiers[p]))
text += '}}'
page = pywikibot.Page(site, 'Template:Number of qualifiers by property')
page.put(text, summary='upd', minorEdit=False)

# write [[Template:Number of references by property]]
text = '{{#switch:{{{1}}}\n'
keys = list(references.keys())
keys.sort(key=lambda x: int(x[1:]))
for p in keys:
    text += '|{}={}\n'.format(p[1:], str(references[p]))
text += '}}'
page = pywikibot.Page(site, 'Template:Number of references by property')
page.put(text, summary='upd', minorEdit=False)

# write [[Gratisdata:Database reports/List of properties/Top100]]
header = 'A list of the top 100 [[Gratisdata:Glossary#property|properties]] by quantity of item pages that link to them. Data as of <onlyinclude>{0}</onlyinclude>.\n\n{{| class="wikitable sortable plainlinks" style="width:100%%; margin:auto;"\n|-\n! Property !! Quantity of item pages\n'
table_row = '|-\n| {{{{P|{0}}}}} || [//gratisdata.miraheze.org/wiki/Special:WhatLinksHere/Property:{0}?namespace=0 {1}]\n'
footer = '|}\n\n[[Category:Properties]]\n[[Category:Gratisdata statistics]]'
sorted = sorted(total.items(), key=lambda item: item[1], reverse=True)
content = ''
for m in sorted[:100]:
    content += table_row.format(m[0], m[1])
text = header.format(time.strftime("%Y-%m-%d %H:%M (%Z)")) + content + footer
page = pywikibot.Page(site, 'Gratisdata:Database reports/List of properties/Top100')
page.put(text, summary='upd', minorEdit=False)
