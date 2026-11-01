-- Business analysis queries (MySQL 8.0+). Run after sql/load_data.sql.
USE sales_profit_db;

-- Q1. Overall KPIs
SELECT ROUND(SUM(d.sales_amount), 2) AS total_sales,
       ROUND(SUM(d.profit), 2) AS total_profit,
       ROUND(SUM(d.profit) / SUM(d.sales_amount) * 100, 2) AS profit_margin_pct,
       COUNT(DISTINCT o.order_id) AS total_orders,
       COUNT(DISTINCT o.customer_id) AS total_customers,
       ROUND(SUM(d.sales_amount) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM order_details d
JOIN orders o ON d.order_id = o.order_id;

-- Q2. Monthly sales and profit trend
SELECT DATE_FORMAT(o.order_date, '%Y-%m') AS month,
       ROUND(SUM(d.sales_amount), 2) AS sales, ROUND(SUM(d.profit), 2) AS profit
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY month;

-- Q3. Category-wise sales, profit and margin
SELECT p.category, ROUND(SUM(d.sales_amount), 2) AS sales, ROUND(SUM(d.profit), 2) AS profit,
       ROUND(SUM(d.profit) / SUM(d.sales_amount) * 100, 2) AS margin_pct
FROM order_details d
JOIN products p ON d.product_id = p.product_id
GROUP BY p.category
ORDER BY sales DESC;

-- Q4. Region-wise sales with share of total
SELECT o.region, ROUND(SUM(d.sales_amount), 2) AS sales,
       ROUND(SUM(d.sales_amount) / (SELECT SUM(sales_amount) FROM order_details) * 100, 2) AS share_pct
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
GROUP BY o.region
ORDER BY sales DESC;

-- Q5. Top 10 best-selling products
SELECT p.product_name, p.category, SUM(d.quantity) AS units_sold,
       ROUND(SUM(d.sales_amount), 2) AS sales, ROUND(SUM(d.profit), 2) AS profit
FROM order_details d
JOIN products p ON d.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY sales DESC
LIMIT 10;

-- Q6. Top 10 customers by sales
SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(d.sales_amount), 2) AS sales, ROUND(SUM(d.profit), 2) AS profit
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY sales DESC
LIMIT 10;

-- Q7. Discount impact on margin
SELECT d.discount, COUNT(*) AS order_lines, ROUND(SUM(d.sales_amount), 2) AS sales,
       ROUND(SUM(d.profit) / SUM(d.sales_amount) * 100, 2) AS margin_pct
FROM order_details d
GROUP BY d.discount
ORDER BY d.discount;

-- Q8. Filtered analysis (WHERE): Electronics in the West region during 2024
SELECT p.product_name, ROUND(SUM(d.sales_amount), 2) AS sales, ROUND(SUM(d.profit), 2) AS profit
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
JOIN products p ON d.product_id = p.product_id
WHERE p.category = 'Electronics' AND o.region = 'West'
  AND o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY p.product_name
ORDER BY sales DESC;

-- Q9. High-value customers (HAVING): total sales above 10,000
SELECT c.customer_id, c.customer_name, ROUND(SUM(d.sales_amount), 2) AS total_sales
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING SUM(d.sales_amount) > 10000
ORDER BY total_sales DESC;

-- Q10. Year-wise sales and profit by region
SELECT YEAR(o.order_date) AS year, o.region,
       ROUND(SUM(d.sales_amount), 2) AS sales, ROUND(SUM(d.profit), 2) AS profit
FROM order_details d
JOIN orders o ON d.order_id = o.order_id
GROUP BY YEAR(o.order_date), o.region
ORDER BY year, sales DESC;
