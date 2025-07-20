
DROP TABLE IF EXISTS floorsheet;
CREATE TABLE floorsheet (
    symbol TEXT,
    rate DOUBLE,
    quantity INTEGER,
    amount DOUBLE,
    transaction_date TEXT,
    broker TEXT
);
