CREATE TABLE Position (
    position_id   INT          PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    UNIQUE (name),
    CONSTRAINT chk_position_name CHECK (name IN ('Менеджер', 'Бухгалтер', 'Товаровед', 'Заведующий фирмой'))
);

CREATE TABLE Bank (
    bank_id         INT          PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    license_number  VARCHAR(100) NOT NULL,
    address         VARCHAR(100),
    country         VARCHAR(60),
    UNIQUE (name),
    UNIQUE (license_number),
    CONSTRAINT chk_bank_country CHECK (country IN ('Казахстан', 'США', 'Россия', 'Евросоюз', 'Китай', 'Великобритания'))
);
 
CREATE TABLE Currency (
    currency_id  INT          PRIMARY KEY,
    country      VARCHAR(60),
    description  VARCHAR(200),
    CONSTRAINT chk_currency_country CHECK (country IN ('Казахстан', 'США', 'Россия', 'Евросоюз', 'Китай', 'Великобритания'))
);
 
CREATE TABLE Employee (
    employee_id     INT          PRIMARY KEY,
    position_id     INT          NOT NULL,
    passport_number VARCHAR(100) NOT NULL,
    iin             BIGINT       NOT NULL,
    full_name       VARCHAR(50)  NOT NULL,
    gender          VARCHAR(10)  NOT NULL,
    phone           VARCHAR(16),
    login           VARCHAR(50),
    password        VARCHAR(50),
    UNIQUE (passport_number),
    UNIQUE (iin),
    CONSTRAINT chk_employee_gender CHECK (gender IN ('М', 'Ж')),
    CONSTRAINT chk_employee_phone  CHECK (phone ~ '^\+?[0-9]{7,15}$'),
    FOREIGN KEY (position_id) REFERENCES Position (position_id)
);
 
CREATE TABLE Currency_Rate (
    rate_id           INT            PRIMARY KEY,
    id_base_currency  INT            NOT NULL,
    id_quote_currency INT            NOT NULL,
    rate_date         DATE           NOT NULL,
    rate_value        NUMERIC(18,6)  NOT NULL,
    CONSTRAINT chk_rate_value            CHECK (rate_value > 0),
    CONSTRAINT chk_rate_diff_currencies  CHECK (id_base_currency <> id_quote_currency),
    CONSTRAINT chk_rate_date             CHECK (rate_date <= CURRENT_DATE),
    UNIQUE (id_base_currency, id_quote_currency, rate_date)
    FOREIGN KEY (id_base_currency)  REFERENCES Currency (currency_id),
    FOREIGN KEY (id_quote_currency) REFERENCES Currency (currency_id)
);
 
CREATE TABLE Buyer_Company (
    company_id        INT          PRIMARY KEY,
    parent_company_id INT,
    name              VARCHAR(100) NOT NULL,
    license_number    VARCHAR(100) NOT NULL,
    legal_address     VARCHAR(100),
    country           VARCHAR(60),
    category          VARCHAR(100),
    UNIQUE (name),
    UNIQUE (license_number),
    CONSTRAINT chk_company_no_self_ref CHECK (parent_company_id <> company_id),
    CONSTRAINT chk_company_country CHECK (country IN ('Казахстан', 'США', 'Россия', 'Евросоюз', 'Китай', 'Великобритания')),
    CONSTRAINT chk_company_category    CHECK (category IN ('Магазин', 'Оптовик', 'Предприятие', 'Сферы обслуживания', 'ИП')),
    FOREIGN KEY (parent_company_id) REFERENCES Buyer_Company (company_id)
);
 
CREATE TABLE Product (
    product_id   INT            PRIMARY KEY,
    currency_id  INT            NOT NULL,
    employee_id  INT            NOT NULL,
    price        NUMERIC(18,6)  NOT NULL,
    CONSTRAINT chk_product_price CHECK (price > 0),
    FOREIGN KEY (currency_id) REFERENCES Currency (currency_id),
    FOREIGN KEY (employee_id) REFERENCES Employee (employee_id)
);
 
CREATE TABLE Invoice (
    invoice_id        INT  PRIMARY KEY,
    currency_id       INT  NOT NULL,
    company_id        INT  NOT NULL,
    employee_id       INT  NOT NULL,
    registration_date DATE,
    payment_date      DATE,
    CONSTRAINT chk_invoice_reg_date     CHECK (registration_date <= CURRENT_DATE),
    CONSTRAINT chk_invoice_payment_date CHECK (payment_date >= registration_date),
    FOREIGN KEY (currency_id) REFERENCES Currency      (currency_id),
    FOREIGN KEY (company_id)  REFERENCES Buyer_Company (company_id),
    FOREIGN KEY (employee_id) REFERENCES Employee      (employee_id)
);
 
CREATE TABLE Invoice_Product (
    invoice_id  INT NOT NULL,
    product_id  INT NOT NULL,
    PRIMARY KEY (invoice_id, product_id),
    FOREIGN KEY (invoice_id) REFERENCES Invoice (invoice_id),
    FOREIGN KEY (product_id) REFERENCES Product (product_id)
);
 
CREATE TABLE Goods_Receipt_Document (
    document_id  INT PRIMARY KEY,
    employee_id  INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employee (employee_id)
);
 
CREATE TABLE Goods_Receipt (
    document_id  INT NOT NULL,
    product_id   INT NOT NULL,
    quantity     INT NOT NULL,
    CONSTRAINT chk_receipt_quantity CHECK (quantity BETWEEN 1 AND 1000000),
    PRIMARY KEY (document_id, product_id),
    FOREIGN KEY (document_id) REFERENCES Goods_Receipt_Document (document_id),
    FOREIGN KEY (product_id)  REFERENCES Product                (product_id)
);
 
CREATE TABLE Bank_Account (
    account_id  INT          PRIMARY KEY,
    company_id  INT          NOT NULL,
    currency_id INT          NOT NULL,
    bank_id     INT          NOT NULL,
    employee_id INT          NOT NULL,
    name        VARCHAR(100) NOT NULL,
    category    VARCHAR(100),
    UNIQUE (name),
    CONSTRAINT chk_account_category CHECK (category IN ('сберегательный', 'расчётный', 'корреспондентский')),
    FOREIGN KEY (company_id)  REFERENCES Buyer_Company (company_id),
    FOREIGN KEY (currency_id) REFERENCES Currency      (currency_id),
    FOREIGN KEY (bank_id)     REFERENCES Bank          (bank_id),
    FOREIGN KEY (employee_id) REFERENCES Employee      (employee_id)
);
 
CREATE TABLE IPO (
    ipo_id              INT            PRIMARY KEY,
    company_id          INT            NOT NULL,
    account_id          INT            NOT NULL,
    employee_id         INT            NOT NULL,
    invoice_id          INT            NOT NULL,
    ipo_number          VARCHAR(100),
    total_amount        NUMERIC(18,6),
    registration_date   DATE,
    UNIQUE (ipo_number),
    CONSTRAINT chk_ipo_total_amount  CHECK (total_amount > 0),
    CONSTRAINT chk_ipo_reg_date      CHECK (registration_date <= CURRENT_DATE),
    CONSTRAINT chk_ipo_number_format CHECK (ipo_number ~ '^[A-Z0-9\-]{3,50}$'),
    FOREIGN KEY (company_id)  REFERENCES Buyer_Company (company_id),
    FOREIGN KEY (account_id)  REFERENCES Bank_Account  (account_id),
    FOREIGN KEY (employee_id) REFERENCES Employee       (employee_id),
    FOREIGN KEY (invoice_id)  REFERENCES Invoice        (invoice_id)
);



drop table if exists IPO cascade;
drop table if exists bank_account cascade;
drop table if exists goods_receipt cascade;
drop table if exists goods_receipt_document cascade;
drop table if exists invoice_product cascade;
drop table if exists invoice cascade;
drop table if exists product cascade;
drop table if exists buyer_company cascade;
drop table if exists currency_rate cascade;
drop table if exists employee cascade;
drop table if exists bank cascade;
drop table if exists currency cascade;
drop table if exists position cascade;