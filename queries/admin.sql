-- ADD PRODUCT
INSERT INTO product
VALUES (5005, 'USB-C Charger', 'Electronics', 1, 19.99);

-- ADD STOCK
INSERT INTO stock
VALUES (5005, 300, 50);

-- UPDATE EXISTING PRODUCT
UPDATE product
SET p_price = 25
WHERE p_productKey = 5005;

-- UPDATE STOCK
UPDATE stock
SET ps_quantity = 20
WHERE ps_storeKey = 300
  AND ps_productKey = 5005;

-- MODIFY TRANSACTION
UPDATE transactions
SET t_transactionstatus = 'C'
WHERE t_transactionKey = 9002;

-- DELETE TRANSACTION
DELETE FROM transactions
WHERE t_transactionKey = 9001;

DELETE FROM transprod
WHERE tp_transactionKey = 9001;

-- DELETE CUSTOMER ACCOUNT
DELETE FROM customer
WHERE c_custKey = 1001;

DELETE FROM transprod
WHERE tp_transactionKey IN (
  SELECT t_transactionKey
  FROM transactions
  WHERE t_custKey = 1001
);

DELETE FROM transactions
WHERE t_custKey = 1001;


-- SEE PRODUCT STOCKS IN A STORE
SELECT p_name, ps_quantity
FROM product
JOIN stock 
  ON ps_productKey = p_productKey
WHERE ps_storeKey = 300;

-- SEE ALL LOW-STOCKED PRODUCTS
SELECT s_name, p_name, ps_quantity
FROM product
JOIN stock
  ON ps_productKey = p_productKey
JOIN store
  ON ps_storeKey = s_storeKey
WHERE ps_quantity < 10;

-- VIEW CUSTOMER TRANSACTIONS
SELECT t_transactionKey
FROM transactions
JOIN customer
  ON c_custKey = t_custKey
WHERE c_custKey = 1005;