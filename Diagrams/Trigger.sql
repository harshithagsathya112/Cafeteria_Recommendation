DELIMITER //
CREATE TRIGGER after_fooditem_main_insert
AFTER INSERT ON fooditem_main
FOR EACH ROW
BEGIN
    INSERT INTO fooditem (ItemName, Price, AvailabilityStatus)
    VALUES (NEW.ItemName, NEW.Price, 1); -- Assuming new items are available by default
END//
DELIMITER ;
DELIMITER //
CREATE TRIGGER after_fooditem_main_update
AFTER UPDATE ON fooditem_main
FOR EACH ROW
BEGIN
    UPDATE fooditem
    SET ItemName = NEW.ItemName,
        Price = NEW.Price
    WHERE ItemName = OLD.ItemName AND Price = OLD.Price;
END//
DELIMITER ;
DELIMITER //
CREATE TRIGGER after_fooditem_main_delete
AFTER DELETE ON fooditem_main
FOR EACH ROW
BEGIN
    DELETE FROM fooditem WHERE ItemName = OLD.ItemName AND Price = OLD.Price;
END//
DELIMITER ;
