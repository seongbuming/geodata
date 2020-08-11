import argparse
import json
from OSMPythonTools.overpass import Overpass

argparser = argparse.ArgumentParser()
argparser.add_argument('--place', '-p', type=str, required=True)
argparser.add_argument('--indent', '-i', type=int, required=False, default=None)
args = argparser.parse_args()

s = 37.4648
w = 126.9607
n = 37.5494
e = 127.1504
count = 0
geodata = {
  'type': 'FeatureCollection',
  'features': []
}

overpass = Overpass()
result = overpass.query(f'\
  area["ISO3166-1:alpha2"="KR"]->.korea;\
  (node(area.korea)["place"="{args.place}"];);\
  out;\
')

elements = result.elements()
for index, node in enumerate(elements):
  print(f'processing... ({index}/{len(elements)})')
  
  breaked = False
  for n in elements:
    if node.id() < n.id(): continue
    elif node.lon() == n.lon() and node.lat() == n.lat() and node.id() > n.id():
      print(f'{node.id()} duplicates with {n.id()}')
      breaked = True
      break
  if breaked: continue

  name = node.tag('name')
  name_ko = node.tag('name:ko')
  name_en = node.tag('name:en')
  if not name:
    if name_ko: name = name_ko
    elif name_en: name = name_en
    else: continue

  feature = {
    'type': 'Feature',
    'geometry': {
      'type': 'Point',
      'coordinates': [node.lon(), node.lat()]
    },
    'properties': {
      'osmid': node.id(),
      'name': name,
      'name:ko': name_ko,
      'name:en': name_en
    }
  }
  geodata['features'].append(feature)
  count = count + 1

with open(f'./data/kr_{args.place}_osm.json', 'w', encoding='utf-8') as json_file:
  dump = json.dumps(geodata, indent=args.indent, ensure_ascii=False)
  json_file.write(dump)
  print(f'{count} nodes saved.')