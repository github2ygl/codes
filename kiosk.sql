-- DROP DATABASE if exists kiosk;

CREATE DATABASE if not exists kiosk;
Use kiosk;

-- Create the Product table
CREATE TABLE Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    stock INT NOT NULL
);

-- Create the Order table
CREATE TABLE `Order` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    fullfilled VARCHAR(50),
    order_date datetime
);

-- Create the OrderProduct table (Intermediary table for the many-to-many relationship)
CREATE TABLE OrderProduct (
    order_product_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES `Order`(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

insert into product (product_name, stock) value 
('커피', 10),
('녹차', 10),
('홍차', 10),
('핫초콜릿', 10);

commit;



