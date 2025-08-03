## Customer and Product Analysis

This project analyzes customer behavior and product performance using SQL queries on the `stores.db` relational database. It answers key business questions using `CTE`, `correlated subqueries`, and aggregation logic.

---

### Database Overview

The database `stores.db` contains 8 interrelated tables:

* `customers`, `orders`, `payments`: Customer lifecycle
* `products`, `productlines`, `orderdetails`: Product catalog and sales
* `employees`, `offices`: Sales staff and locations
<img width="701" height="560" alt="image" src="https://github.com/user-attachments/assets/06a60e2e-1767-42fb-a05f-b0ea081ea6ca" />

---

### Key Business Questions

1. **Which products should we restock?**
   Identifies products that are both high-performing and low in stock.

2. **How should we tailor marketing by customer behavior?**
   Segments customers by profit contribution to highlight VIPs and re-engagement targets.

3. **How much can we spend to acquire new customers?**
   Combines customer growth trends and average lifetime value (LTV) to inform acquisition budgets.

---

### Techniques Used

* Common Table Expressions (CTEs)
* Correlated subqueries
* Aggregation with `SUM`, `AVG`, `GROUP BY`
* Filtering with `LIMIT`, `ORDER BY`, and `IN`

---




