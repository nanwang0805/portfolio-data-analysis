-- ===========================
-- Database Schema Overview 
-- ===========================

-- productlines: a list of product line categories
--   - One-to-many with products.

-- products: a list of scale model cars
--   - Belongs to productlines.
--   - One-to-many with orderdetails.

-- orderdetails: sales order line for each sales order
--   - Links products and orders.

-- orders: customers' sales orders
--   - Belongs to customers.
--   - One-to-many with orderdetails.

-- customers: customer data
--   - One-to-many with orders and payments.
--   - Linked to sales rep (employees).

-- payments: customers' payment records
--   - Belongs to customers.

-- employees: all employee information
--   - Linked to office and reportsTo (self).
--   - One-to-many with customers.

-- offices: sales office information
--   - One-to-many with employees.

-- ====================================

SELECT  "Customers" AS  table_name, 
                   (SELECT  COUNT(*) FROM pragma_table_info('Customers')) AS num_attributes,
				   (SELECT COUNT(*) FROM customers) AS num_rows
UNION ALL 
SELECT  "Products" ,
                   (SELECT  COUNT(*) FROM pragma_table_info('Products')) ,
				   (SELECT COUNT(*) FROM products) 
UNION ALL 	
SELECT  "ProductLines" ,
                   (SELECT  COUNT(*) FROM pragma_table_info('ProductLines')),
				   (SELECT COUNT(*) FROM productlines) 	   
UNION ALL 		   
SELECT  "Orders" ,
                   (SELECT  COUNT(*) FROM pragma_table_info('Orders')),
				   (SELECT COUNT(*) FROM orders) 
UNION ALL 			   		   
SELECT  "OrderDetails" , 
                   (SELECT  COUNT(*) FROM pragma_table_info('OrderDetails')) ,
				   (SELECT COUNT(*) FROM orderdetails) 
UNION ALL 		   
SELECT  "Payments" , 
                   (SELECT  COUNT(*) FROM pragma_table_info('Payments')) ,
				   (SELECT COUNT(*) FROM payments) 
UNION ALL 		   
SELECT  "Employees" , 
                   (SELECT  COUNT(*) FROM pragma_table_info('Employees')) ,
				   (SELECT COUNT(*) FROM employees) 
UNION ALL 			   
SELECT  "Offices" AS  table_name, 
                   (SELECT  COUNT(*) FROM pragma_table_info('Offices')) ,
				   (SELECT COUNT(*) FROM offices) ;
 
 -- Question 1: Which Products Should We Order More of or Less of?
 WITH 
 performance_table AS(
  SELECT productCode, SUM(quantityOrdered*priceEach) as product_performance
      FROM orderdetails
    GROUP BY productCode
    ORDER BY product_performance DESC
     LIMIT 10
),

lowstock_table AS(
  SELECT p.productCode, p.productName, p.productLine,
       (SELECT SUM(quantityOrdered)
             FROM orderdetails AS od
         WHERE p.productCode = od.productCode)/p.quantityInStock AS lowstock
   FROM products AS p
 GROUP BY p.productCode
 ORDER BY lowstock DESC
  LIMIT 10)
 
 SELECT productName, productLine
     FROM lowstock_table
 WHERE productCode IN (SELECT productCode FROM performance_table);
 -- Classic cars are the priority for restocking. They sell frequently, and they are the highest-performance products.

-- Question 2: How Should We Match Marketing and Communication Strategies to Customer Behavior?
-- find the top five VIP customers
WITH 
profit_table AS(
 SELECT o.customerNumber, SUM(od.quantityOrdered * (od.priceEach - p.buyPrice)) AS profit
    FROM products AS p
      JOIN orderdetails AS od
           ON p.productCode = od.productCode
      JOIN orders AS o
           ON od.orderNumber = o.orderNumber
   GROUP BY o.customerNumber)

SELECT c.contactLastName, c.contactFirstName, c.city, c.country, pt.profit
    FROM customers AS c
      JOIN profit_table AS pt
           ON c.customerNumber = pt.customerNumber
  ORDER BY pt.profit DESC
   LIMIT 5;
 
 -- find the top five least-engaged customers
WITH 
profit_table AS(
 SELECT o.customerNumber, SUM(od.quantityOrdered * (od.priceEach - p.buyPrice)) AS profit
    FROM products AS p
      JOIN orderdetails AS od
           ON p.productCode = od.productCode
      JOIN orders AS o
           ON od.orderNumber = o.orderNumber
   GROUP BY o.customerNumber)
 
 SELECT c.contactLastName, c.contactFirstName, c.city, c.country, pt.profit
    FROM customers AS c
      JOIN profit_table AS pt
           ON c.customerNumber = pt.customerNumber
  ORDER BY pt.profit
   LIMIT 5;
   
-- Question 3: How Much Can We Spend on Acquiring New Customers?
 --  step 1: the number of new customers arriving each month since 2003
 WITH 
payment_with_year_month_table AS (
SELECT *, 
       CAST(SUBSTR(paymentDate, 1,4) AS INTEGER)*100 + CAST(SUBSTR(paymentDate, 6,7) AS INTEGER) AS year_month
  FROM payments p
),

customers_by_month_table AS (
SELECT p1.year_month, COUNT(*) AS number_of_customers, SUM(p1.amount) AS total
  FROM payment_with_year_month_table p1
 GROUP BY p1.year_month
),

new_customers_by_month_table AS (
SELECT p1.year_month, 
       COUNT(DISTINCT customerNumber) AS number_of_new_customers,
       SUM(p1.amount) AS new_customer_total,
       (SELECT number_of_customers
          FROM customers_by_month_table c
        WHERE c.year_month = p1.year_month) AS number_of_customers,
       (SELECT total
          FROM customers_by_month_table c
         WHERE c.year_month = p1.year_month) AS total
  FROM payment_with_year_month_table p1
 WHERE p1.customerNumber NOT IN (SELECT customerNumber
                                   FROM payment_with_year_month_table p2
                                  WHERE p2.year_month < p1.year_month)
 GROUP BY p1.year_month
)

SELECT year_month, 
       ROUND(number_of_new_customers*100/number_of_customers,1) AS number_of_new_customers_props,
       ROUND(new_customer_total*100/total,1) AS new_customers_total_props
  FROM new_customers_by_month_table;
 -- The number of clients has been decreasing since 2003. This means it makes sense to spend money acquiring new customers.
  
 -- step 2: compute the average of customer profits
 WITH 
profit_table AS(
 SELECT o.customerNumber, SUM(od.quantityOrdered * (od.priceEach - p.buyPrice)) AS profit
    FROM products AS p
      JOIN orderdetails AS od
           ON p.productCode = od.productCode
      JOIN orders AS o
           ON od.orderNumber = o.orderNumber
   GROUP BY o.customerNumber)
   
 SELECT AVG(profit) AS avg_customer_profit
     FROM profit_table;
-- LTV: 39,039.59
-- LTV tells us how much profit an average customer generates during their lifetime with our store. 
-- We can use it to predict our future profit. So, if we get ten new customers next month, we'll earn 390,395 dollars, 
-- and we can decide based on this prediction how much we can spend on acquiring new customers.




