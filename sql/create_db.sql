-- Create Database and Tables for Sales & Profit Analytics
CREATE DATABASE IF NOT EXISTS sales_profit_db;
USE sales_profit_db;

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
  customer_id VARCHAR(20) PRIMARY KEY,
  customer_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(100) UNIQUE,
  category VARCHAR(50),
  unit_cost DECIMAL(10,2),
  unit_price DECIMAL(10,2)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
  order_id VARCHAR(20) PRIMARY KEY,
  order_date DATE,
  customer_id VARCHAR(20),
  region VARCHAR(50),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Order details table
CREATE TABLE IF NOT EXISTS order_details (
  order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id VARCHAR(20),
  product_id INT,
  quantity INT,
  unit_price DECIMAL(10,2),
  discount DECIMAL(5,2) DEFAULT 0,
  sales_amount DECIMAL(12,2),
  profit DECIMAL(12,2),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);
