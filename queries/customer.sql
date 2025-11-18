-- 1. Login verification (name + phone)
SELECT c_custKey
FROM customer
WHERE c_name = 'Fiona'
  AND c_phone = '858-555-5555';

-- 2. Create an order
INSERT INTO transactions (t_transactionKey, t_custKey, t_storeKey, t_transactionstatus, t_totalpayment, t_transactiondate)
VALUES (9100, 1005, 300, 'U', 0.00, DATE('now'));
-- test
SELECT * FROM transactions WHERE t_transactionKey = 9100;

-- 3. Add items to order
INSERT INTO transprod (tp_transactionKey, tp_productKey, tp_quantity)
VALUES (9100, 5005, 2);   -- UCM Hat x2
-- test
SELECT * FROM transprod WHERE tp_transactionKey = 9100;

-- 4. the amount of items you added from your store inventory
UPDATE stock
SET ps_quantity = ps_quantity - 2
WHERE ps_storeKey = 300 AND ps_productKey = 5005 AND ps_quantity >= 2;
-- test
SELECT * FROM stock WHERE ps_storeKey = 300 AND ps_productKey = 5005;

-- 5. Calculate and update the order total
UPDATE transactions
SET t_totalpayment = (
  SELECT SUM(tp.tp_quantity * p.p_price)
  FROM transprod tp
  JOIN product p ON p.p_productKey = tp.tp_productKey
  WHERE tp.tp_transactionKey = 9100
)
WHERE t_transactionKey = 9100;
-- test
SELECT * FROM transactions WHERE t_transactionKey = 9100;

-- 6. Payment/Order Confirmation (Status C = Completed) 근데 이미 C 야 
UPDATE transactions
SET t_transactionstatus = 'C'
WHERE t_transactionKey = 9100;
-- test
SELECT * FROM transactions WHERE t_transactionKey = 9100;

-- 7. Order Details
SELECT p.p_name, p.p_price, tp.tp_quantity, (p.p_price * tp.tp_quantity) AS line_total
FROM transprod tp
JOIN product p ON p.p_productKey = tp.tp_productKey
WHERE tp.tp_transactionKey = 9100;

-- 8. Customer's order history (5 most recent)
SELECT t_transactionKey, t_storeKey, t_transactionstatus, t_totalpayment, t_transactiondate
FROM transactions
WHERE t_custKey = 1005
ORDER BY t_transactiondate DESC, t_transactionKey DESC
LIMIT 5;

-- 9.Show products only from stores in my city (personalized)
SELECT st.s_name AS store, p.p_name, ps.ps_quantity, p.p_price
FROM customer c
JOIN city ci     ON ci.ci_cityKey = c.c_cityKey
JOIN campus ca   ON ca.ca_cityKey = ci.ci_cityKey
JOIN store st    ON st.s_campusKey = ca.ca_campuskey
JOIN stock ps    ON ps.ps_storeKey = st.s_storeKey
JOIN product p   ON p.p_productKey = ps.ps_productKey
WHERE c.c_custKey = 1002
ORDER BY store, p.p_name;
