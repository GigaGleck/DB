from faker import Faker
import random
import re
from datetime import date, timedelta

fake = Faker('ru_RU')
random.seed()
Faker.seed(random.seed())

def sql_str(val):
    if val is None:
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def sql_val(val):
    if val is None:
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, date):
        return f"'{val}'"
    return sql_str(val)

def rand_date_past(days=730):
    return date.today() - timedelta(days=random.randint(1, days))

def rand_phone():
    digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return '+7' + digits[:10]

def insert(table, rows):
    if not rows:
        return ''
    cols = ', '.join(rows[0].keys())
    lines = [f'-- {table}']
    for row in rows:
        vals = ', '.join(sql_val(v) for v in row.values())
        lines.append(f'INSERT INTO {table} ({cols}) VALUES ({vals}) ON CONFLICT DO NOTHING;')
    lines.append('')
    return '\n'.join(lines)

N_POSITIONS     = 4
N_BANKS         = 5
N_CURRENCIES    = 6
N_EMPLOYEES     = 15
N_RATES         = 20
N_COMPANIES     = 12
N_PRODUCTS      = 20
N_INVOICES      = 15
N_DOCUMENTS     = 10
N_ACCOUNTS      = 12
N_IPOS          = 10

GENDERS         = ['М', 'Ж']
COUNTRIES       = ['Казахстан', 'США', 'Россия', 'Евросоюз', 'Китай', 'Великобритания']
COMPANY_CATS    = ['Магазин', 'Оптовик', 'Предприятие', 'Сферы обслуживания', 'ИП']
ACCOUNT_CATS    = ['сберегательный', 'расчётный', 'корреспондентский']

# Пул названий товаров (для нового столбца Product.name)
PRODUCT_NAMES = [
    'Ноутбук', 'Смартфон', 'Планшет', 'Монитор', 'Клавиатура',
    'Компьютерная мышь', 'Принтер', 'Сканер', 'Веб-камера', 'Наушники',
    'Колонки', 'Жёсткий диск', 'SSD-накопитель', 'Оперативная память', 'Видеокарта',
    'Процессор', 'Материнская плата', 'Блок питания', 'Корпус ПК', 'Сетевой роутер',
    'Сетевой коммутатор', 'USB-флешка', 'Кабель HDMI', 'Источник бесперебойного питания', 'Проектор',
    'Графический планшет', 'Картридж', 'Док-станция', 'Микрофон', 'Кулер для процессора',
]
MAX_SALE_QTY = 50   # макс. количество единиц товара в одной строке накладной



position_names = ['Менеджер', 'Бухгалтер', 'Товаровед', 'Заведующий фирмой']
positions = [
    {'position_id': i + 1, 'name': position_names[i]}
    for i in range(N_POSITIONS)
]



bank_names = ['Halyk Bank', 'Kaspi Bank', 'Jusan Bank', 'ForteBank', 'Bereke Bank']
banks = [
    {
        'bank_id':        i + 1,
        'name':           bank_names[i],
        'license_number': f'LIC-{1000 + i}',
        'address':        fake.address().replace('\n', ', '),
        'country':        random.choice(COUNTRIES),
    }
    for i in range(N_BANKS)
]



currencies_data = [
    ('Казахстан',  'Казахстанский тенге'),
    ('США',        'Доллар США'),
    ('Россия',     'Российский рубль'),
    ('Евросоюз',   'Евро'),
    ('Китай',      'Китайский юань'),
    ('Великобритания', 'Британский фунт стерлингов'),
]
currencies = [
    {'currency_id': i + 1, 'country': currencies_data[i][0], 'description': currencies_data[i][1]}
    for i in range(N_CURRENCIES)
]
currency_ids = [c['currency_id'] for c in currencies]



used_iins       = set()
used_passports  = set()
used_logins     = set()

def gen_iin():
    while True:
        iin = random.randint(800101_000001, 991231_999999)
        if iin not in used_iins:
            used_iins.add(iin)
            return iin

def gen_passport():
    while True:
        p = fake.bothify('??#######').upper()
        if p not in used_passports:
            used_passports.add(p)
            return p

def gen_login(name):
    base = re.sub(r'[^a-z]', '', name.lower().replace(' ', '_'))[:10] or 'user'
    candidate = base
    suffix = 1
    while candidate in used_logins:
        candidate = f'{base}{suffix}'
        suffix += 1
    used_logins.add(candidate)
    return candidate

employees = []
for i in range(N_EMPLOYEES):
    gender = random.choice(GENDERS)
    full_name = fake.name_male() if gender == 'М' else fake.name_female()
    login = gen_login(fake.user_name())
    employees.append({
        'employee_id':     i + 1,
        'position_id':     random.randint(1, N_POSITIONS),
        'passport_number': gen_passport(),
        'iin':             gen_iin(),
        'full_name':       full_name[:50],
        'gender':          gender,
        'phone':           rand_phone(),
        'login':           login,
        'password':        fake.sha256()[:50],
    })



rates = []
used_rate_pairs = set()
for i in range(N_RATES):
    while True:
        base  = random.choice(currency_ids)
        quote = random.choice(currency_ids)
        d     = rand_date_past(365)
        key   = (base, quote, str(d))
        if base != quote and key not in used_rate_pairs:
            used_rate_pairs.add(key)
            break
    rates.append({
        'rate_id':           i + 1,
        'id_base_currency':  base,
        'id_quote_currency': quote,
        'rate_date':         d,
        'rate_value':        round(random.uniform(0.001, 500.0), 6),
    })



companies = []
used_company_names = set()
used_company_lics  = set()

for i in range(N_COMPANIES):
    while True:
        name = fake.company()[:100]
        if name not in used_company_names:
            used_company_names.add(name)
            break
    lic = f'BIN-{200000 + i}'
    parent = None
    if i > 3 and random.random() < 0.3:
        parent = random.randint(1, i)   # ссылка на уже созданную компанию
    companies.append({
        'company_id':        i + 1,
        'parent_company_id': parent,
        'name':              name,
        'license_number':    lic,
        'legal_address':     fake.address().replace('\n', ', ')[:100],
        'country':           random.choice(COUNTRIES),
        'category':          random.choice(COMPANY_CATS),
        'phone':             rand_phone(),
    })

company_ids = [c['company_id'] for c in companies]



products = []
product_name_pool = random.sample(PRODUCT_NAMES, min(N_PRODUCTS, len(PRODUCT_NAMES)))
for i in range(N_PRODUCTS):
    prod_name = product_name_pool[i] if i < len(product_name_pool) else f'Товар №{i + 1}'
    products.append({
        'product_id':  i + 1,
        'name':        prod_name,
        'currency_id': random.choice(currency_ids),
        'employee_id': random.randint(1, N_EMPLOYEES),
        'price':       round(random.uniform(100.0, 500000.0), 6),
    })

product_ids = [p['product_id'] for p in products]



invoices = []
for i in range(N_INVOICES):
    reg_date = rand_date_past(365)
    pay_date = reg_date + timedelta(days=random.randint(0, 90))
    if pay_date > date.today():
        pay_date = date.today()
    invoices.append({
        'invoice_id':        i + 1,
        'currency_id':       random.choice(currency_ids),
        'company_id':        random.choice(company_ids),
        'employee_id':       random.randint(1, N_EMPLOYEES),
        'registration_date': reg_date,
        'payment_date':      pay_date,
    })

invoice_ids = [inv['invoice_id'] for inv in invoices]



inv_products = []
used_inv_prod = set()
for inv in invoices:
    n = random.randint(1, 4)
    chosen = random.sample(product_ids, min(n, len(product_ids)))
    for pid in chosen:
        key = (inv['invoice_id'], pid)
        if key not in used_inv_prod:
            used_inv_prod.add(key)
            inv_products.append({
                'invoice_id': inv['invoice_id'],
                'product_id': pid,
                'quantity':   random.randint(1, MAX_SALE_QTY),
            })



grd_docs = [
    {'document_id': i + 1, 'employee_id': random.randint(1, N_EMPLOYEES)}
    for i in range(N_DOCUMENTS)
]
doc_ids = [d['document_id'] for d in grd_docs]



receipts = []
used_receipts = set()
for doc in grd_docs:
    n = random.randint(1, 5)
    chosen = random.sample(product_ids, min(n, len(product_ids)))
    for pid in chosen:
        key = (doc['document_id'], pid)
        if key not in used_receipts:
            used_receipts.add(key)
            receipts.append({
                'document_id': doc['document_id'],
                'product_id':  pid,
                'quantity':    random.randint(1, 500),
            })



accounts = []
used_acc_names = set()
for i in range(N_ACCOUNTS):
    while True:
        acc_name = f'Счёт {fake.bothify("??###").upper()}'
        if acc_name not in used_acc_names:
            used_acc_names.add(acc_name)
            break
    accounts.append({
        'account_id':  i + 1,
        'company_id':  random.choice(company_ids),
        'currency_id': random.choice(currency_ids),
        'bank_id':     random.randint(1, N_BANKS),
        'employee_id': random.randint(1, N_EMPLOYEES),
        'name':        acc_name,
        'category':    random.choice(ACCOUNT_CATS),
    })

account_ids = [a['account_id'] for a in accounts]



ipos = []
used_ipo_numbers = set()
for i in range(N_IPOS):
    while True:
        ipo_num = f'IPO-{random.randint(1000, 9999)}'
        if ipo_num not in used_ipo_numbers:
            used_ipo_numbers.add(ipo_num)
            break
    reg_date = rand_date_past(365)
    ipos.append({
        'ipo_id':            i + 1,
        'company_id':        random.choice(company_ids),
        'account_id':        random.choice(account_ids),
        'employee_id':       random.randint(1, N_EMPLOYEES),
        'invoice_id':        random.choice(invoice_ids),
        'ipo_number':        ipo_num,
        'total_amount':      round(random.uniform(10000.0, 10_000_000.0), 6),
        'registration_date': reg_date,
    })



output = []

output.append(insert('Position',              positions))
output.append(insert('Bank',                  banks))
output.append(insert('Currency',              currencies))
output.append(insert('Employee',              employees))
output.append(insert('Currency_Rate',         rates))
output.append(insert('Buyer_Company',         companies))
output.append(insert('Product',               products))
output.append(insert('Invoice',               invoices))
output.append(insert('Invoice_Product',       inv_products))
output.append(insert('Goods_Receipt_Document', grd_docs))
output.append(insert('Goods_Receipt',         receipts))
output.append(insert('Bank_Account',          accounts))
output.append(insert('IPO',                   ipos))

OUTPUT_FILE = 'insert_data.sql'

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f'Данные записаны в {OUTPUT_FILE}')