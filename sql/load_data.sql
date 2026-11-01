-- Load data into sales_profit_db (MySQL 8.0+). Run sql/create_db.sql first.
USE sales_profit_db;

-- Step 1: staging table (same columns as data/sample_sales.csv)
DROP TABLE IF EXISTS sales_staging;
CREATE TABLE sales_staging (
  OrderID VARCHAR(20), OrderDate DATE, CustomerID VARCHAR(20), CustomerName VARCHAR(100),
  Product VARCHAR(100), Category VARCHAR(50), Region VARCHAR(50), Quantity INT,
  UnitPrice DECIMAL(10,2), Discount DECIMAL(5,2), SalesAmount DECIMAL(12,2), Profit DECIMAL(12,2)
);

-- Step 2: import the CSV into sales_staging (choose ONE option)
-- Option A: MySQL Workbench -> right-click sales_staging -> Table Data Import Wizard -> select data/sample_sales.csv
-- Option B: LOAD DATA (edit the path; needs local_infile enabled: SET GLOBAL local_infile = 1;)
-- The CSV has Windows line endings (\r\n). If your copy uses \n only, change LINES TERMINATED BY accordingly.
-- LOAD DATA LOCAL INFILE 'C:/path/to/data/sample_sales.csv'
-- INTO TABLE sales_staging
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\r\n'
-- IGNORE 1 ROWS;

-- Step 3: clear target tables (makes this script safe to re-run)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE order_details;
TRUNCATE TABLE orders;
TRUNCATE TABLE products;
TRUNCATE TABLE customers;
SET FOREIGN_KEY_CHECKS = 1;

-- Step 4: customers - one name per CustomerID (most frequent name, ties alphabetical).
-- The raw CSV has several names for the same CustomerID; the dashboard and Excel use the same rule.
INSERT INTO customers (customer_id, customer_name)
SELECT CustomerID, CustomerName
FROM (
  SELECT CustomerID, CustomerName,
         ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY COUNT(*) DESC, CustomerName ASC) AS rn
  FROM sales_staging
  GROUP BY CustomerID, CustomerName
) t
WHERE rn = 1;

-- Step 5: products. unit_price = average selling price in the data.
-- unit_cost is derived: total cost (SalesAmount - Profit) / total quantity (the CSV has no cost column).
INSERT INTO products (product_name, category, unit_cost, unit_price)
SELECT Product, MIN(Category),
       ROUND(SUM(SalesAmount - Profit) / SUM(Quantity), 2),
       ROUND(AVG(UnitPrice), 2)
FROM sales_staging
GROUP BY Product;

-- Step 6: orders and order details
INSERT INTO orders (order_id, order_date, customer_id, region)
SELECT OrderID, MIN(OrderDate), MIN(CustomerID), MIN(Region)
FROM sales_staging
GROUP BY OrderID;

INSERT INTO order_details (order_id, product_id, quantity, unit_price, discount, sales_amount, profit)
SELECT s.OrderID, p.product_id, s.Quantity, s.UnitPrice, s.Discount, s.SalesAmount, s.Profit
FROM sales_staging s
JOIN products p ON p.product_name = s.Product;

-- Step 7: validation (expected for sample_sales.csv: 1000 orders, 150 customers, 25 products,
-- total sales 1124204.49, total profit 585082.25)
SELECT (SELECT COUNT(*) FROM orders)    AS orders_cnt,
       (SELECT COUNT(*) FROM customers) AS customers_cnt,
       (SELECT COUNT(*) FROM products)  AS products_cnt,
       SUM(sales_amount) AS total_sales, SUM(profit) AS total_profit
FROM order_details;
