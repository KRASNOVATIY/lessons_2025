import logging
import unicodedata
from math import floor
from struct import unpack
from typing import (
    Dict,
    Optional,
    Tuple,
)

RESOURCE_FILE_ID = '0x46444707'
RESOURCE_FILE_EF = 239
DO_NOT_EXPORT = [
    'route_',
    'ctr_',
    'geo_',
    'chm_store',
    'org_banner',
    'back_splash',
    'banner_',
    'road_',
    'interchange_',
    'logo_picture',
    'pk_',
]
DATA_DIR: Dict = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def read_long(f):
    v = f.read(4)
    v = unpack('i', v)
    return v[0]


def read_byte(f):
    v = f.read(1)
    v = unpack('c', v)
    return int(v[0][0])


def read_packed_value(f):
    size = read_byte(f)
    val = size

    if size >= 0xF0:
        size = read_byte(f)
        size2 = read_byte(f)
        size3 = read_byte(f)
        size4 = read_byte(f)
        val = (size << 24) | (size2 << 16) | (size3 << 8) | size4

    elif size >= 0xE0:
        size2 = read_byte(f)
        size3 = read_byte(f)
        size4 = read_byte(f)
        val = (size ^ 0xE0) << 24 | size2 << 16 | (size3 << 8) | size4

    elif size >= 0xC0:
        size2 = read_byte(f)
        size3 = read_byte(f)
        val = (size ^ 0xC0) << 16 | size2 << 8 | size3

    elif size & 0x80:
        size2 = read_byte(f)
        val = (size ^ 0x80) << 8 | size2

    return val


def read_string(f, string_length: int) -> str:
    if string_length > 0:
        contents = f.read(string_length)
        parsed_string = ''.join([chr(content) for content in contents])
        return parsed_string
    return ''


def get_packed_value(tbl: str) -> Tuple[int, str]:
    size = ord(tbl[:1])
    tbl = tbl[1:]
    val = size

    if size >= 0xF0:
        size = ord(tbl[:1])
        tbl = tbl[1:]

        size2 = ord(tbl[:1])
        tbl = tbl[1:]

        size3 = ord(tbl[:1])
        tbl = tbl[1:]

        size4 = ord(tbl[:1])
        tbl = tbl[1:]

        val = (size << 24) | size2 << 16 | (size3 << 8) | size4

    elif size >= 0xE0:
        size2 = ord(tbl[:1])
        tbl = tbl[1:]

        size3 = ord(tbl[:1])
        tbl = tbl[1:]

        size4 = ord(tbl[:1])
        tbl = tbl[1:]

        val = (size ^ 0xE0) << 24 | size2 << 16 | (size3 << 8) | size4

    elif size >= 0xC0:
        size2 = ord(tbl[:1])
        tbl = tbl[1:]

        size3 = ord(tbl[:1])
        tbl = tbl[1:]

        val = (size ^ 0xC0) << 16 | size2 << 8 | size3

    elif size & 0x80:
        size2 = ord(tbl[:1])
        tbl = tbl[1:]
        val = (size ^ 0x80) << 8 | size2

    return val, tbl


def unpack_wide_string(temp_str: str) -> str:
    x1, temp_str = get_packed_value(temp_str)
    x2, temp_str = get_packed_value(temp_str)

    z = ''
    for _ in range(0, x2):
        z += temp_str[:1]
        z += chr(0)
        temp_str = temp_str[1:]

    if len(temp_str):
        arr = []
        count = ord(temp_str[:1])
        temp_str = temp_str[1:]
        mcount = count

        for _ in range(0, mcount):
            v = ord(temp_str[:1])
            temp_str = temp_str[1:]
            arr.append(v)

        iterable = 0
        while len(temp_str):
            v = ord(temp_str[:1])
            temp_str = temp_str[1:]
            count = floor(v / mcount)
            offset = v % mcount
            if count == 0:
                for i in range(iterable, len(z), 2):
                    z = z[: i + 1] + chr(arr[offset]) + z[i + 2:]
            else:
                for _ in range(0, count):
                    z = z[: iterable + 1] + chr(arr[offset]) + z[iterable + 2:]
                    iterable += 2

    return z


def dexor_table(main_name, field_name, data, need_decode=1):
    copy = data

    if field_name != '':
        if not DATA_DIR.get(main_name):
            DATA_DIR[main_name] = {}
        DATA_DIR[main_name][field_name] = data

    tbllen, data = get_packed_value(data)

    if tbllen == 0:
        return ''

    dat = ''
    an_len, data = get_packed_value(data)
    data = data[an_len:]
    an_len, data = get_packed_value(data)

    start = tbllen + 1

    for i in range(start, start + an_len):
        ch = copy[i]
        if need_decode == 1:
            dat += chr(ord(ch) ^ 0xC5)
            copy = copy[:i] + chr(ord(copy[i]) ^ 0xC5) + copy[i + 1:]
        else:
            dat += ch

    return dat


def process_table(name, data):
    for item in DO_NOT_EXPORT:
        if name.find(item) == 0:
            return

    tbllen, data = get_packed_value(data)
    tbl = data[:tbllen]
    data = data[tbllen:]

    while len(tbl) > 0:
        an_len = ord(tbl[:1])
        tbl = tbl[1:]
        chunk = tbl[:an_len]
        tbl = tbl[an_len:]
        if chunk == 'data':
            return

        size, tbl = get_packed_value(tbl)
        p = data[:size]
        data = data[size:]

        dexor_table(name, chunk, p, 0)


def export_field(name, field, need_decode=1, pair_decode=0):
    afield = []

    dat = DATA_DIR[name][field]

    if not len(dat):
        raise Exception('Internal Core Error')

    dat = dexor_table(name, field, dat, need_decode)

    if pair_decode == 10:
        i = 1
        for k in range(0, len(dat), 4):
            temp = dat[k: k + 4]
            temp = unpack('L', temp)
            afield.append(temp[1])
            i += 1

        return afield

    if pair_decode == 1:
        i = 1
        k = 0
        while k < len(dat):
            temp = dat[k: k + 12]
            init_len = len(temp)
            repeat, temp = get_packed_value(temp)
            value, temp = get_packed_value(temp)

            for _ in range(0, repeat):
                afield.append(value)
                i += 1
            x = init_len - len(temp)
            k = k + x

        return afield

    if pair_decode == 4:
        i = 1
        k = 0
        while k < len(dat):
            temp = dat[k: k + 22]
            init_len = len(temp)
            repeat, temp = get_packed_value(temp)
            nm = init_len - len(temp)

            an_len, temp = get_packed_value(temp)
            xlen, temp = get_packed_value(temp)

            afield[repeat] = xlen
            k = k + an_len + nm + 1

        return afield

    if pair_decode == 2:
        k = 0
        while k < len(dat):
            temp = dat[k: k + 12]
            init_len = len(temp)
            value, temp = get_packed_value(temp)
            afield.append(value)
            g = init_len - len(temp)
            k = k + g

        return afield

    if pair_decode == 3:
        k = 0

        while k < len(dat):
            temp = dat[k: k + 12]
            init_len = len(temp)
            repeat, temp = get_packed_value(temp)
            nm = init_len - len(temp)

            an_len, temp = get_packed_value(temp)

            if an_len == 0:
                x = ''
            elif an_len > 0x7F:
                x = dat[k + nm: k + nm + an_len + 2]
                x = unpack_wide_string(x)
                an_len += 1
            else:
                x = dat[k + nm: k + nm + an_len + 1]
                x = unpack_wide_string(x)

            for _ in range(0, repeat):
                x = (
                    unicodedata.normalize('NFKD', x)
                        .encode('utf-8')
                        .decode('utf-16le', errors='ignore')
                )
                afield.append(x)

            k = k + an_len + nm + 1
        return afield

    k = 0

    while k < len(dat):
        temp = dat[k: k + 5]
        an_len, temp = get_packed_value(temp)

        if an_len == 0:
            x = ''
        elif an_len > 0x7F:
            x = dat[k: k + an_len + 2]
            x = unpack_wide_string(x)
            an_len += 1
        else:
            x = dat[k: k + an_len + 1]
            x = unpack_wide_string(x)

        x = unicodedata.normalize('NFKD', x).encode('utf-8').decode('utf-16le', errors='ignore')
        afield.append(x)
        k = k + an_len + 1

    return afield


def decode(fb):
    dump = {}

    file_id = read_long(fb)
    ef = read_byte(fb)

    if hex(file_id) != RESOURCE_FILE_ID or ef != RESOURCE_FILE_EF:
        return None

    read_long(fb)
    read_long(fb)

    read_packed_value(fb)
    read_packed_value(fb)
    read_packed_value(fb)
    read_packed_value(fb)

    tbllen = read_byte(fb)
    tbl = read_string(fb, tbllen)

    logger.debug('Export step 1. First while')

    while len(tbl) > 0:
        tbl_length = ord(tbl[:1])

        tbl = tbl[1:]
        chunk = tbl[0:tbl_length]
        tbl = tbl[tbl_length:]
        size, tbl = get_packed_value(tbl)

        temp = read_string(fb, size)
        inset = ['name', 'cpt', 'fbn', 'lang', 'stat']
        if chunk in inset:
            temp = unpack_wide_string(temp)

    temp = read_packed_value(fb)
    tbllen = read_packed_value(fb)
    tbl = read_string(fb, tbllen)
    root = 0

    logger.debug('Export step 2. Second while')

    while len(tbl) > 0:
        tbl_length = ord(tbl[:1])

        tbl = tbl[1:]
        chunk = tbl[0:tbl_length]
        tbl = tbl[tbl_length:]
        size, tbl = get_packed_value(tbl)
        if chunk == 'data':
            root = fb.tell()

        temp = read_string(fb, size)

    fb.seek(root)
    tbllen = read_packed_value(fb)
    tbl = read_string(fb, tbllen)

    logger.debug('Export step 3. Third while')

    while len(tbl) > 0:
        string_len = ord(tbl[:1])
        tbl = tbl[1:]

        chunk = tbl[:string_len]
        tbl = tbl[string_len:]

        size, tbl = get_packed_value(tbl)
        data = read_string(fb, size)
        process_table(chunk, data)

    logger.debug('Export step 4. org')
    dump['orgid'] = export_field('org', 'id', 0, 2)
    dump['org'] = export_field('org', 'name', 1)

    logger.debug('Export step 5. city')
    dump['city'] = export_field('city', 'name', 1)

    logger.debug('Export step 6. street')
    dump['street'] = export_field('street', 'name', 1)
    dump['street_city'] = export_field('street', 'city', 0, 1)

    logger.debug('Export step 7. fil_contact')
    dump['fil_contact_fil'] = export_field('fil_contact', 'fil', 0, 1)
    dump['fil_contact_phone'] = export_field('fil_contact', 'phone')
    dump['fil_contact_eaddr'] = export_field('fil_contact', 'eaddr', 1)
    dump['fil_contact_type'] = export_field('fil_contact', 'type', 0, 2)

    logger.debug('Export step 8. fil_org')
    dump['fil_org'] = export_field('fil', 'org', 0, 1)

    logger.debug('Export step 9. fil_address')
    dump['fil_address_fil'] = export_field('fil_address', 'fil', 0, 1)
    dump['fil_address_address'] = export_field('fil_address', 'address', 0, 2)

    logger.debug('Export step 10. address_elem')
    dump['address_elem'] = export_field('address_elem', 'street', 0, 1)
    dump['building'] = export_field('address_elem', 'building')

    logger.debug('Export step 11. org_rub')
    dump['orgrub_rub'] = export_field('org_rub', 'rub', 0, 2)
    dump['orgrub_org'] = export_field('org_rub', 'org', 0, 1)

    logger.debug('Export step 12. fil_rub')
    dump['filrub_fil'] = export_field('fil_rub', 'fil', 0, 1)
    dump['filrub_rub'] = export_field('fil_rub', 'rub', 0, 2)

    logger.debug('Export step 13. rub3')
    dump['rub3_name'] = export_field('rub3', 'name', 1)
    dump['rub3_rub2'] = export_field('rub3', 'rub2', 0, 1)

    logger.debug('Export step 14. rub2')
    dump['rub2_name'] = export_field('rub2', 'name', 1)
    dump['rub2_rub1'] = export_field('rub2', 'rub1', 0, 1)

    logger.debug('Export step 15. rub1')
    dump['rub1_name'] = export_field('rub1', 'name', 1)

    # link phones to organizations
    for key, val in enumerate(dump['fil_contact_fil']):
        if not dump.get('fil_contact_fil2'):
            dump['fil_contact_fil2'] = {}
        if not dump['fil_contact_fil2'].get(val - 1):
            dump['fil_contact_fil2'][val - 1] = []

        dump['fil_contact_fil2'][val - 1].append(key)

    # link address to organizations
    for key, val in enumerate(dump['fil_address_fil']):
        if not dump.get('fil_address_fil2'):
            dump['fil_address_fil2'] = {}

        dump['fil_address_fil2'][val - 1] = key

    # link rubric to organization
    for key, val in enumerate(dump['orgrub_org']):
        if not dump.get('orgrub_org2'):
            dump['orgrub_org2'] = {}
        if not dump['orgrub_org2'].get(val - 1):
            dump['orgrub_org2'][val - 1] = []

        dump['orgrub_org2'][val - 1].append(key)

    for key, val in enumerate(dump['filrub_fil']):
        if not dump.get('filrub_fil2'):
            dump['filrub_fil2'] = {}
        if not dump['filrub_fil2'].get(val - 1):
            dump['filrub_fil2'][val - 1] = []

        dump['filrub_fil2'][val - 1].append(key)

    # map exported info to orgID
    results = []
    for key, fil in enumerate(dump['fil_org']):
        phones = []
        emails = []
        name = dump['org'][fil - 1]
        org_id = dump['orgid'][fil - 1]
        addr: Optional[str] = None
        try:
            row = dump['fil_address_fil2'][key]
            row = dump['fil_address_address'][row]
            building = dump['building'][row - 1]
            street_row = dump['address_elem'][row - 1]
            street_name = dump['street'][street_row - 1]
            street_id = dump['street_city'][street_row - 1]
            city_name = dump['city'][street_id - 1]
            addr = ', '.join([city_name.split()[0], street_name, building])
        except (KeyError, IndexError):
            addr = None

        rows = dump['fil_contact_fil2'].get(key, [])

        for row in rows:
            typeof = chr(dump['fil_contact_type'][row])
            if typeof == 'p':
                phone = dump['fil_contact_phone'][row]
                if phone != '':
                    phones.append(phone)

            eaddr = dump['fil_contact_eaddr'][row]
            if typeof == 'm' and len(eaddr) > 0:
                emails.append(eaddr)

        r3 = []
        r2 = []
        r1 = []
        rows = dump['orgrub_org2'].get(fil - 1, [])
        rows2 = dump['filrub_fil2'].get(key, [])

        for row in rows:
            rubid = dump['orgrub_rub'][row]
            r3.append(dump['rub3_name'][rubid - 1])

            r2id = dump['rub3_rub2'][rubid - 1]
            r2.append(dump['rub2_name'][r2id - 1])

            r1id = dump['rub2_rub1'][r2id - 1]
            r1.append(dump['rub1_name'][r1id - 1])
        for row in rows2:
            rubid = dump['filrub_rub'][row]
            r3.append(dump['rub3_name'][rubid - 1])

            r2id = dump['rub3_rub2'][rubid - 1]
            r2.append(dump['rub2_name'][r2id - 1])

            r1id = dump['rub2_rub1'][r2id - 1]
            r1.append(dump['rub1_name'][r1id - 1])

        r3 = sorted([*{*r3}])
        r2 = sorted([*{*r2}])
        r1 = sorted([*{*r1}])

        result_json = {
            'OID': org_id,
            'Name': name,
            'Phone': ', '.join(phones),
            'Email': ', '.join(emails),
            'R1': ', '.join(r1),
            'R2': ', '.join(r2),
            'R3': ', '.join(r3),
            'Adr': addr,
        }

        results.append(result_json)

    return results


if __name__ == "__main__":
    with open('a.dgdat', 'rb') as f:
        r = decode(f)
    assert len(r) == 6694
    assert r[0] == {
        'OID': 1219298653,
        'Name': 'А Авто Друг16, выездная служба',
        'Phone': '+7-967-379-00-80',
        'Email': '',
        'R1': 'Аварийные / справочные / экстренные службы, Автосервис / Автотовары, Коммунальные / бытовые / ритуальные услуги',
        'R2': 'Аварийные / справочные / экстренные службы, Автосервис, Бытовые услуги',
        'R3': 'Вскрытие / обслуживание замков, дверей, Выездная техническая помощь на дороге, Эвакуация автомобилей',
        'Adr': None
    }
