SELECT '-- 1. View products by campus (UCM) --';
SELECT st.s_name AS store, p.p_name AS product, p.p_price, st.s_storeKey, ps.ps_quantity
FROM store st
JOIN stock ps   ON ps.ps_storeKey = st.s_storeKey
JOIN product p  ON p.p_productKey = ps.ps_productKey
WHERE st.s_campusKey = 30
ORDER BY store, p.p_name;
.print ''

SELECT '-- 2. Search for products by keyword --';
SELECT p_productKey, p_name, p_category, p_price
FROM product
WHERE p_name LIKE '%Hoodie%'
ORDER BY p_price DESC;
.print ''

SELECT '-- 3. Category + Size + Price Range Filter --';
SELECT p_productKey, p_name, p_size, p_price
FROM product
WHERE p_category = 'APPAREL'
  AND p_size = 'L'
  AND p_price BETWEEN 40 AND 80
ORDER BY p_price;
.print ''

SELECT '-- 4. Out of stock items at a specific store (<10) --';
SELECT st.s_name, p.p_name, ps.ps_quantity
FROM stock ps
JOIN store st   ON st.s_storeKey = ps.ps_storeKey
JOIN product p  ON p.p_productKey = ps.ps_productKey
WHERE ps.ps_storeKey = 300
  AND ps.ps_quantity < 10
ORDER BY ps.ps_quantity;
.print ''

SELECT '-- 5. Top N in price --';
SELECT p_productKey, p_name, p_price
FROM product
ORDER BY p_price DESC
LIMIT 5;
.print ''

SELECT '-- 6. Sing up registration --';
INSERT INTO customer (c_custKey, c_name, c_address, c_cityKey, c_phone, c_balance)
VALUES (1015, 'Paul', '77 College Rd', 3, '209-999-0000', 0.00);
-- test
SELECT * FROM customer WHERE c_custKey = 1015;
