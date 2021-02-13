DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS locationn;
DROP TABLE IF EXISTS movement;
DROP TABLE IF EXISTS report;

CREATE TABLE product (
    prod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prod_name TEXT NOT NULL UNIQUE,
    qty INTEGER
);

CREATE TABLE locationn (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL UNIQUE
);

CREATE TABLE movement (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestampp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    from_l TEXT,
    to_l TEXT,
    prod_name TEXT NOT NULL,
    qty INTEGER NOT NULL,
    FOREIGN KEY(prod_name) REFERENCES product(prod_name),
    FOREIGN KEY(from_l) REFERENCES locationn(location_name),
    FOREIGN KEY(to_l) REFERENCES locationn(location_name)
);

CREATE TABLE report (
    p TEXT NOT NULL,
    wh TEXT NOT NULL,
    qty INTEGER NOT NULL
);

CREATE TRIGGER IF NOT EXISTS qty_zero
                    AFTER UPDATE ON report
                    FOR EACH ROW
                    WHEN new.qty=0
                    BEGIN
                        DELETE from report  WHERE p =new.p AND wh=new.wh;
                    END;
