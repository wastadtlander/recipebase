-- Adminer 4.8.1 MySQL 5.5.5-10.3.22-MariaDB-log dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `Comments`;
CREATE TABLE `Comments` (
  `Body` varchar(10000) NOT NULL,
  `UserID` varchar(36) NOT NULL,
  `Recipe` varchar(36) NOT NULL,
  KEY `UserID` (`UserID`),
  KEY `Recipe` (`Recipe`),
  CONSTRAINT `Comments_ibfk_7` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `Comments_ibfk_9` FOREIGN KEY (`Recipe`) REFERENCES `Recipe` (`RecipeID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Comments` (`Body`, `UserID`, `Recipe`) VALUES
('I love this recipe for your waffles in 2023 :)',	'2382da03-6eed-11ee-95c8-96fc48e250ac',	'031953e1-6ef1-11ee-95c8-96fc48e250ac'),
('I also love this recipe for waffles in 2023!',	'1798bce1-6eed-11ee-95c8-96fc48e250ac',	'031953e1-6ef1-11ee-95c8-96fc48e250ac');

DROP TABLE IF EXISTS `Rating`;
CREATE TABLE `Rating` (
  `Value` tinyint(1) NOT NULL,
  `RatingID` varchar(36) NOT NULL,
  `UserID` varchar(36) NOT NULL,
  `RecipeID` varchar(36) NOT NULL,
  PRIMARY KEY (`RatingID`),
  KEY `UserID` (`UserID`),
  KEY `RecipeID` (`RecipeID`),
  CONSTRAINT `Rating_ibfk_10` FOREIGN KEY (`RecipeID`) REFERENCES `Recipe` (`RecipeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `Rating_ibfk_8` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Rating` (`Value`, `RatingID`, `UserID`, `RecipeID`) VALUES
(5,	'7cd7f8fc-6f00-11ee-95c8-96fc48e250ac',	'2382da03-6eed-11ee-95c8-96fc48e250ac',	'031953e1-6ef1-11ee-95c8-96fc48e250ac'),
(4,	'91f8f686-6f00-11ee-95c8-96fc48e250ac',	'1798bce1-6eed-11ee-95c8-96fc48e250ac',	'031953e1-6ef1-11ee-95c8-96fc48e250ac');

DROP TABLE IF EXISTS `Recipe`;
CREATE TABLE `Recipe` (
  `Title` varchar(255) NOT NULL,
  `Type` enum('Asian','Italian','other') DEFAULT NULL,
  `Text` varchar(10000) NOT NULL,
  `RecipeID` varchar(36) NOT NULL,
  `UserID` varchar(36) NOT NULL,
  PRIMARY KEY (`RecipeID`),
  KEY `UserID` (`UserID`),
  CONSTRAINT `Recipe_ibfk_2` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Recipe` (`Title`, `Type`, `Text`, `RecipeID`, `UserID`) VALUES
('[NEW] My famous waffles *2023*',	'other',	'Updated my old waffle recipe with improvements from the comments. It\'s very different, here are all the steps *imagine there are a bunch of steps here*',	'031953e1-6ef1-11ee-95c8-96fc48e250ac',	'c709d09f-6eed-11ee-95c8-96fc48e250ac'),
('Sausage rolls',	'Italian',	'Here is how you make a sausage rolls!\\nTo make them, follow these instructions fr. This is just dummy data. Imagine these are steps to make a flan:',	'0bfb3b1d-6eef-11ee-95c8-96fc48e250ac',	'337ccde6-6eee-11ee-95c8-96fc48e250ac'),
('Fast pasta',	'Italian',	'PAsta in a hurry:\\nHere is the pasta recipe',	'0fe6e2db-6ef1-11ee-95c8-96fc48e250ac',	'c709d09f-6eed-11ee-95c8-96fc48e250ac'),
('Burgers',	NULL,	'1. patty\\n2. meat\\n3. vegetables\\n4. that\'s it. No other ingredients. Imagine I went into more detail than I\'m currently doing because this is just dummy data',	'2a75bfea-6ef0-11ee-95c8-96fc48e250ac',	'337ccde6-6eee-11ee-95c8-96fc48e250ac'),
('The best Ramen you\'ll ever have',	'Asian',	'I haven\'t seen anyone talk about this amazing ramen recipe, so I\'m sharing it here. It should only take a few minutes to make, too, which is good if you\'re in a hurry',	'34b5593d-6ef1-11ee-95c8-96fc48e250ac',	'c709d09f-6eed-11ee-95c8-96fc48e250ac'),
('Hot dogs',	NULL,	'Here is how you make a flan!\\nI don\'t actually know what\'s in a flan. This is just dummy data. Imagine these are steps to make a flan:',	'37b775f4-6ef0-11ee-95c8-96fc48e250ac',	'dd05001a-6eec-11ee-95c8-96fc48e250ac'),
('Ice cream on a stick',	NULL,	'Stir up some milk, I think. Then freeze it and put it on a stick. Now you\'ve made ice cream on a stick seriously',	'4809f39c-6ef0-11ee-95c8-96fc48e250ac',	'dd05001a-6eec-11ee-95c8-96fc48e250ac'),
('Roasted goose',	'other',	'Take a goose and roast it. ',	'4fd85a7e-6ef1-11ee-95c8-96fc48e250ac',	'a3c7c9b0-6eed-11ee-95c8-96fc48e250ac'),
('Beef',	NULL,	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'56574787-6ef1-11ee-95c8-96fc48e250ac',	'a3c7c9b0-6eed-11ee-95c8-96fc48e250ac'),
('Ice cream not on a stick',	NULL,	'Do the same thing as in my recipe for ice cream on a stick (pinned on my profile) but don\'t put the ice cream on a stick at the end',	'5c3a120c-6ef0-11ee-95c8-96fc48e250ac',	'cf7afe5f-6eed-11ee-95c8-96fc48e250ac'),
('Cake!!!!',	NULL,	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'5f279a57-6ef1-11ee-95c8-96fc48e250ac',	'a3c7c9b0-6eed-11ee-95c8-96fc48e250ac'),
('Green eggs and ham',	'Asian',	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'69a7980c-6ef1-11ee-95c8-96fc48e250ac',	'a3c7c9b0-6eed-11ee-95c8-96fc48e250ac'),
('3D Country',	NULL,	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'712dbd7f-6ef1-11ee-95c8-96fc48e250ac',	'a3c7c9b0-6eed-11ee-95c8-96fc48e250ac'),
('Corn dogs',	NULL,	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'8a8fab46-6ef1-11ee-95c8-96fc48e250ac',	'2382da03-6eed-11ee-95c8-96fc48e250ac'),
('Creamed corn',	'other',	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'92056546-6ef1-11ee-95c8-96fc48e250ac',	'2382da03-6eed-11ee-95c8-96fc48e250ac'),
('Meatloaf',	'other',	'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',	'9eb9de0c-6ef1-11ee-95c8-96fc48e250ac',	'2382da03-6eed-11ee-95c8-96fc48e250ac'),
('I don\'t have a name for this but I made it myself',	'other',	'It\'s a concoction of vinegar, vinegar, wine, winegar, and wine',	'daca394d-6ef0-11ee-95c8-96fc48e250ac',	'c709d09f-6eed-11ee-95c8-96fc48e250ac'),
('[OUTDATED] MY famous waffles',	'other',	'Put these jawns in the microwave for 4 minutes and serve with ketchup and mustard!',	'e576147c-6ef0-11ee-95c8-96fc48e250ac',	'c709d09f-6eed-11ee-95c8-96fc48e250ac'),
('Flan',	'other',	'Here is how you make a flan!\\nI don\'t actually know what\'s in a flan. This is just dummy data. Imagine these are steps to make a flan:\\n1.Step 1\\n2. Step 2',	'ef1f8a0f-6eee-11ee-95c8-96fc48e250ac',	'337ccde6-6eee-11ee-95c8-96fc48e250ac'),
('Chicken nuggets',	'other',	'Put these jawns in the microwave for 4 minutes and serve with ketchup and mustard!',	'fec50b65-6eef-11ee-95c8-96fc48e250ac',	'337ccde6-6eee-11ee-95c8-96fc48e250ac');

DROP TABLE IF EXISTS `RecipeImage`;
CREATE TABLE `RecipeImage` (
  `Image` varchar(255) NOT NULL,
  `RecipeID` varchar(36) NOT NULL,
  PRIMARY KEY (`RecipeID`,`Image`),
  CONSTRAINT `RecipeImage_ibfk_2` FOREIGN KEY (`RecipeID`) REFERENCES `Recipe` (`RecipeID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `RecipeImage` (`Image`, `RecipeID`) VALUES
('/031953e1-6ef1-11ee-95c8-96fc48e250ac/file1.png',	'031953e1-6ef1-11ee-95c8-96fc48e250ac'),
('/031953e1-6ef1-11ee-95c8-96fc48e250ac/file2.png',	'031953e1-6ef1-11ee-95c8-96fc48e250ac'),
('/031953e1-6ef1-11ee-95c8-96fc48e250ac/file3.png',	'031953e1-6ef1-11ee-95c8-96fc48e250ac'),
('/2a75bfea-6ef0-11ee-95c8-96fc48e250ac/file1.png',	'2a75bfea-6ef0-11ee-95c8-96fc48e250ac'),
('/2a75bfea-6ef0-11ee-95c8-96fc48e250ac/file2.png',	'2a75bfea-6ef0-11ee-95c8-96fc48e250ac');

DROP TABLE IF EXISTS `User`;
CREATE TABLE `User` (
  `Name` varchar(64) NOT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `Profile Picture` binary(1) DEFAULT NULL,
  `User Type` enum('Admin','User') NOT NULL,
  `UserID` varchar(36) NOT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `User` (`Name`, `Email`, `Profile Picture`, `User Type`, `UserID`) VALUES
('real paul rudd',	'paulruddofficial@gmail.com',	NULL,	'User',	'03057324-6eee-11ee-95c8-96fc48e250ac'),
('MinecraftCreeper55',	'joshsandman@hotmail.com',	NULL,	'User',	'09112b8c-6eed-11ee-95c8-96fc48e250ac'),
('Zarina',	'zarinamyers01@gmail.com',	NULL,	'User',	'153cc18b-6eee-11ee-95c8-96fc48e250ac'),
('Nancy Wheeler',	'iluvdogs@comcast.net',	NULL,	'Admin',	'1798bce1-6eed-11ee-95c8-96fc48e250ac'),
('MintyFresh',	'greenpenguin@gmail.com',	NULL,	'User',	'2382da03-6eed-11ee-95c8-96fc48e250ac'),
('Anthony Laraway',	'anthony.laraway@gmail.com',	NULL,	'User',	'2dbf3b2b-6eed-11ee-95c8-96fc48e250ac'),
('This name is taken',	'electricliz999@gmail.com',	NULL,	'User',	'337ccde6-6eee-11ee-95c8-96fc48e250ac'),
('Domoto',	'domoto_domoto3@gmail.com',	NULL,	'User',	'3acdb172-6eee-11ee-95c8-96fc48e250ac'),
('Laurie B',	'brooksworthlaurie1@gmail.com',	NULL,	'User',	'524c06d7-6eee-11ee-95c8-96fc48e250ac'),
('17th Row',	'the17throw@gmail.com',	NULL,	'User',	'5a022c06-6eee-11ee-95c8-96fc48e250ac'),
('Max',	'Maxine1980__@gmail.com',	NULL,	'User',	'8a4beba9-6eee-11ee-95c8-96fc48e250ac'),
('Max',	'maxthejedi@gmail.com',	NULL,	'User',	'961141ae-6eee-11ee-95c8-96fc48e250ac'),
('London',	'londonemail@email.com',	NULL,	'User',	'a3c7c9b0-6eed-11ee-95c8-96fc48e250ac'),
('Jesse1717',	'the_goat_jesse@gmail.com',	NULL,	'User',	'bd5d7ab7-6eed-11ee-95c8-96fc48e250ac'),
('Recipe Base',	'contact@recipebase.com',	NULL,	'Admin',	'c709d09f-6eed-11ee-95c8-96fc48e250ac'),
('Grammar',	'grammar@gmail.com',	NULL,	'User',	'cf7afe5f-6eed-11ee-95c8-96fc48e250ac'),
('John Green',	'john.green@gmail.com',	NULL,	'User',	'dd05001a-6eec-11ee-95c8-96fc48e250ac'),
('Lafayette Geese',	'g.lafa@gmail.com',	NULL,	'User',	'df2cb894-6eed-11ee-95c8-96fc48e250ac'),
('Cameron Winter',	'camw1999@gmail.com',	NULL,	'User',	'e8e9cf4a-6eec-11ee-95c8-96fc48e250ac'),
('LowEra',	'beth.o.l@gmail.com',	NULL,	'User',	'f67bcd73-6eed-11ee-95c8-96fc48e250ac');

-- 2023-10-20 22:24:19
