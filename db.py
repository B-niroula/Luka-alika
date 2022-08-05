import sqlite3 
conn = sqlite3.connect("project.sqlite") 

cursor = conn.cursor()  
sql1 = """DROP TABLE IF EXISTS Hospital;"""  
sqlc = """DROP TABLE IF EXISTS Visitor;""" 
sqld = """DROP TABLE IF EXISTS Agent;""" 
sqlb = """DROP TABLE IF EXISTS Place;"""
sqlg = """DROP TABLE IF EXISTS Visiting;"""
sqlh = """DROP TABLE IF EXISTS Hospital_approval;""" 

sql_query = """
            CREATE TABLE Visitor(
            citizen_id integer PRIMARY KEY,
            visitor_name text NOT NULL, 
            email text NOT NULL,
            phone_number text NOT NULL, 
            address text NOT NULL,
            password text NOT NULL,
            infected integer NOT NULL,
            checked_in   BOOLEAN NOT NULL DEFAULT (0) 
        )""" 
sql_query1 = """
            CREATE TABLE Agent( 
                agent_id integer PRIMARY KEY, 
                username text NOT NULL,
                password text NOT NULL
             )"""  
sql_query2 = """ 
             CREATE TABLE Hospital( 
                 hospital_id text PRIMARY KEY NOT NULL, 
                 username text NOT NULL, 
                 password text NOT NULL
             )
            """  
sql_query3 = """ 
             CREATE TABLE Place( 
                 place_id integer PRIMARY KEY NOT NULL,
                 place_name text NOT NULL,
                 email text NOT NULL,
                 password text NOT NULL,
                 phone_number integer NOT NULL,
                 address text NOT NULL
             )
             """
sql_query4 = """ 
             CREATE TABLE Visiting( 
                 visiting_id integer PRIMARY KEY NOT NULL,
                 citizen_id integer NOT NULL,
                 place_id integer NOT NULL,
                 check_in_time text,
                 check_out_time text,
                 CONSTRAINT fk_visiting
                    FOREIGN KEY (citizen_id) 
                    REFERENCES Visitor (citizen_id)
                    ON DELETE CASCADE
                    FOREIGN KEY (place_id) 
                    REFERENCES Place (place_id)
                    ON DELETE CASCADE

             )
             """  

sql_query5 = """ 
             CREATE TABLE Hospital_approval( 
                 hospital_id text PRIMARY KEY NOT NULL, 
                 username text NOT NULL, 
                 password text NOT NULL
             )
            """  


cursor.execute(sql1) #Deleting the table so that running everytime new database is not duplicated 
cursor.execute(sqlc) 
cursor.execute(sqld) 
cursor.execute(sqlh)  
cursor.execute(sqlb) 
cursor.execute(sqlg)

cursor.execute(sql_query)  
cursor.execute(sql_query1) 
cursor.execute(sql_query2) 
cursor.execute(sql_query3)
cursor.execute(sql_query4)
cursor.execute(sql_query5)

sql = """INSERT INTO Agent(username,password) VALUES(?,?)""" 
sql2 =  """INSERT INTO Hospital(hospital_id,username,password) VALUES(?,?,?)""" 
sql3 = """INSERT INTO Visitor(visitor_name, phone_number, email, address, password, infected) VALUES(?,?,?,?,?,?)"""
sql4 =  """INSERT INTO Place(place_name,email,password,phone_number,address) VALUES(?,?,?,?,?)"""
cursor.execute(sql,("ZERO","12345")) 
cursor.execute(sql,("BRYAN","2004"))  
cursor.execute(sql,("admin","admin"))  
cursor.execute(sql2,(123,"appaji","12345")) 
cursor.execute(sql2,(456,"hari","CITY")) 
cursor.execute(sql2,(100,"wang","what"))
cursor.execute(sql3,("wang", "1234", "n@outlook.com", "campusring 0", "120", 0))
cursor.execute(sql3,("Suyash", "1234", "lanji", "campusring 0.1", "1000", 0))
cursor.execute(sql3,("Jerry", "3456", "themouse@tom", "campusring 0.01", "999", 0))
cursor.execute(sql4,("q", "q", "q", "q", "q"))

conn.commit()



            
