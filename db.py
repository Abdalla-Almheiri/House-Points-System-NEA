def database():
    import sqlite3

    conn = sqlite3.connect("House points")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS Student;")
    cursor.execute("DROP TABLE IF EXISTS Teacher;")
    cursor.execute("DROP TABLE IF EXISTS House;")
    cursor.execute("DROP TABLE IF EXISTS House_points_record;")
    cursor.execute("DROP TABLE IF EXISTS Purchase_token;")
    cursor.execute("DROP TABLE IF EXISTS Token;")
    cursor.execute("DROP TABLE IF EXISTS Owned_tokens;")
    cursor.execute("DROP TABLE IF EXISTS Notifs;")

    #Teacher table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teacher (
            teacher_id INTEGER,
            password_hash VARCHAR(100),
            title VARCHAR(4),
            first_name VARCHAR(15),
            last_name VARCHAR(15),
            subject VARCHAR(20),
            PRIMARY KEY (teacher_id)
        );
    ''')

    #House table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS House (
            house_id INTEGER,
            house_name VARCHAR(8),
            house_totalpoints INTEGER,
            house_leaderboard_position INTEGER,
            PRIMARY KEY (house_id)
        );
    ''')

    #Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notifs (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            change VARCHAR(8),
            not_seen INTEGER,
            FOREIGN KEY (record_id) REFERENCES House_points_record(record_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id)  
        );    
    ''')

    #Token table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Token (
            token_id INTEGER,
            token_name VARCHAR(20),
            point_cost INTEGER,
            description VARCHAR(100),
            PRIMARY KEY (token_id)
        );
    ''')

    #Student table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Student (
            student_id INTEGER,
            password_hash VARCHAR(100),
            first_name VARCHAR(15),
            last_name VARCHAR(15),
            grade VARCHAR(3),
            house_id INTEGER,
            total_points INTEGER,
            leaderboard_position INTEGER,
            position_in_house INTEGER,
            PRIMARY KEY (student_id),
            FOREIGN KEY (house_id) REFERENCES House(house_id)
        );
    ''')

    #Owned_tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Owned_tokens (
            student_id INTEGER,
            token_id INTEGER,
            quantity INTEGER,
            last_purchase_date DATETIME,
            allowed_purchase_date DATETIME,
            PRIMARY KEY (student_id, token_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (token_id) REFERENCES Token(token_id)
        );
    ''')

    #House_points_record table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS House_points_record (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            teacher_id INTEGER,
            points VARCHAR(5),
            date_created DATETIME,
            reason VARCHAR(200),
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id)
        );
    ''')

    #Purchase_token table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Purchase_token (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            token_id INTEGER,
            purchase_date DATETIME,
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (token_id) REFERENCES Token(token_id)
        );
    ''')

    #Adding houses
    cursor.execute("INSERT INTO House (house_id, house_name, house_totalpoints) VALUES (1,'Gazelles', 1000);")
    cursor.execute("INSERT INTO House (house_id, house_name, house_totalpoints) VALUES (2,'Oryxes', 1500);")
    cursor.execute("INSERT INTO House (house_id, house_name, house_totalpoints) VALUES (3,'Foxes', 0);")
    cursor.execute("INSERT INTO House (house_id, house_name, house_totalpoints) VALUES (4,'Falcons', 0);")

    #Adding tokens
    cursor.execute("INSERT INTO Token (token_id, token_name, point_cost, description) VALUES (1, 'Dress Code Exemption', 750, 'Student is allowed to spend one\nday wearing non-uniform clothing\n( 750 points )')")
    cursor.execute("INSERT INTO Token (token_id, token_name, point_cost, description) VALUES ( 2, 'Cafeteria coupon', 250, 'Student recieves 1 free meal\nfrom the school cafeteria\n( 250 points )')")
    cursor.execute("INSERT INTO Token (token_id, token_name, point_cost, description) VALUES ( 3, '1 day off', 1500, 'Student is allowed one day\nof registered abscence\n( 1500 points )')")

    #Adding default values for tests
    cursor.execute("INSERT INTO Student (student_id, first_name, last_name, password_hash, grade, house_id, total_points, leaderboard_position, position_in_house) VALUES (1899,'Arthur','Morgan','95d7a3b9d43b191522e8a65d828e3ed3c31b97978ab699f4f2c3fa55436dd9e5', '13A', 1, 1000, NULL, NULL);")
    cursor.execute("INSERT INTO Student (student_id, first_name, last_name, password_hash, grade, house_id, total_points, leaderboard_position, position_in_house) VALUES (1,'John','Doe','6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', '13C', 2, 1500, NULL, NULL);")
    cursor.execute("INSERT INTO Teacher (teacher_id, password_hash, title, first_name, last_name, subject) VALUES (1, '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'Mr.', 'Walter', 'White','Chemistry')")
    cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, allowed_purchase_date) VALUES (1899, 1, 0, NULL, NULL)")
    cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, allowed_purchase_date) VALUES (1899, 2, 0, NULL, NULL)")
    cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, allowed_purchase_date) VALUES (1899, 3, 0, NULL, NULL)")
    cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, allowed_purchase_date) VALUES (1, 1, 0, '2024-04-09', '2024-06-08')")
    cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, allowed_purchase_date) VALUES (1, 2, 0, '2024-04-09', '2024-05-09')")
    cursor.execute("INSERT INTO Owned_tokens (student_id, token_id, quantity, last_purchase_date, allowed_purchase_date) VALUES (1, 3, 0, NULL, NULL)")

    conn.commit()
    conn.close()

    #Note: If updating database,
    #do NOT
    #FORGET
    #TO RE-ADD
    #THE FUNCTION
    #!!!!!!!!!!!!!!!!!!!
