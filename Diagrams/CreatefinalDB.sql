CREATE DATABASE CafeteriaDB;
USE CafeteriaDB;

-- Create role table
CREATE TABLE role (
    RoleID INT AUTO_INCREMENT PRIMARY KEY,
    RoleName VARCHAR(50)
);

-- Create user table
CREATE TABLE user (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeID VARCHAR(50),
    Name VARCHAR(100),
    RoleID INT,
    Password VARCHAR(50),
    FOREIGN KEY (RoleID) REFERENCES role(RoleID)
);

-- Create fooditem_main table
CREATE TABLE fooditem_main (
    LookupID INT AUTO_INCREMENT PRIMARY KEY,
    ItemName VARCHAR(255),
    Price DECIMAL(10, 2)
);

-- Create fooditem table
CREATE TABLE fooditem (
    FoodItemID INT AUTO_INCREMENT PRIMARY KEY,
    ItemName VARCHAR(100),
    Price DECIMAL(10, 2),
    AvailabilityStatus TINYINT(1)
);

-- Create menu table
CREATE TABLE menu (
    MenuID INT AUTO_INCREMENT PRIMARY KEY,
    Date DATE,
    MealType ENUM('Breakfast', 'Lunch', 'Dinner'),
    FoodItemID INT,
    FOREIGN KEY (FoodItemID) REFERENCES fooditem(FoodItemID)
);

-- Create recommendation table
CREATE TABLE recommendation (
    RecommendationID INT AUTO_INCREMENT PRIMARY KEY,
    Date DATE,
    MealType ENUM('Breakfast', 'Lunch', 'Dinner'),
    FoodItemID INT,
    FOREIGN KEY (FoodItemID) REFERENCES fooditem(FoodItemID)
);

-- Create votetable table
CREATE TABLE votetable (
    PollID INT AUTO_INCREMENT PRIMARY KEY,
    VoteDate DATE,
    FoodItemID INT,
    UserID INT,
    FOREIGN KEY (FoodItemID) REFERENCES fooditem(FoodItemID),
    FOREIGN KEY (UserID) REFERENCES user(UserID)
);

-- Create feedback table
CREATE TABLE feedback (
    FeedbackID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    Comment TEXT,
    Rating INT,
    FeedbackDate DATE,
    FoodItemID INT,
    FOREIGN KEY (UserID) REFERENCES user(UserID),
    FOREIGN KEY (FoodItemID) REFERENCES fooditem(FoodItemID)
);

-- Create notification table
CREATE TABLE notification (
    NotificationID INT AUTO_INCREMENT PRIMARY KEY,
    Message TEXT,
    NotificationDate DATE,
    IsRead TINYINT(1)
);


