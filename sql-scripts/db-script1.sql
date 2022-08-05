CREATE TABLE Visitor( 
 citizen_id 	INT(10) NOT NULL,
 visitor_name 	VARCHAR(200) NOT NULL,
 address 		VARCHAR(200) NOT NULL,
 phone_number 	VARCHAR(30) NOT NULL,
 device_ID 		VARCHAR(200) NOT NULL,
 infected 		INT(1) NOT NULL DEFAULT 0,

 PRIMARY KEY (citizen_id)
);

CREATE TABLE Place(
 place_id 	INT(10) NOT NULL,
 place_name	VARCHAR(200) NOT NULL,
 address 	VARCHAR(200) NOT NULL,
 QRcode 	VARCHAR(5000) NOT NULL,
 
 PRIMARY KEY (place_id)
);

CREATE TABLE VisitorToPlace(
 citizen_id 	INT(10) NOT NULL,
 place_id 		INT(10) NOT NULL,
 entry_date 	DATE NOT NULL,
 entry_time 	VARCHAR(6) NOT NULL,
 exit_date 		DATE NOT NULL,
 exit_time 		VARCHAR(6) NOT NULL,

 PRIMARY KEY (citizen_id, place_id)
);

CREATE TABLE Agent(
 agent_id 		INT(10) NOT NULL,
 username 		VARCHAR(200) NOT NULL,
 password 		VARCHAR(200) NOT NULL,

 PRIMARY KEY (agent_id)
);

CREATE TABLE Hospital(
 hospital_id 		INT(10) NOT NULL,
 username 		VARCHAR(200) NOT NULL,
 password 		VARCHAR(200) NOT NULL,

 PRIMARY KEY (hospital_id)
);
