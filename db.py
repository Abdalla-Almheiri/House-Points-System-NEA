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
    cursor.execute("DROP TABLE IF EXISTS Student_token_ownership;")

    #Teacher table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teacher (
            teacher_id INTEGER,
            password VARCHAR(20),
            first_name VARCHAR(15),
            last_name VARCHAR(15),
            PRIMARY KEY (teacher_id)
        );
    ''')

    #House table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS House (
            house_id INTEGER,
            house_name VARCHAR(8),
            PRIMARY KEY (house_id)
        );
    ''')

    #Token table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Token(
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
            password VARCHAR(20),
            first_name VARCHAR(15),
            last_name VARCHAR(15),
            grade VARCHAR(3),
            house_id INTEGER,
            total_points INTEGER,
            leaderboard_position INTEGER,
            PRIMARY KEY (student_id),
            FOREIGN KEY (house_id) REFERENCES House(house_id)
        );
    ''')

    #Student_Token_Ownership table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Student_token_ownership (
            student_id INTEGER,
            token_id INTEGER,
            quantity INTEGER,
            PRIMARY KEY (student_id, token_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (token_id) REFERENCES Token(token_id)
        );
    ''')

    #House_points_record table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS House_points_record (
            record_id INTEGER,
            student_id INTEGER,
            teacher_id INTEGER,
            points INTEGER,
            date_created DATETIME,
            PRIMARY KEY (record_id),
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
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (1,'Gazelles');")
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (2,'Oryxes');")
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (3,'Foxes');")
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (4,'Falcons');")

    #Adding tokens
    cursor.execute("INSERT INTO Token (token_id, token_name, point_cost, description) VALUES (1, 'Dress Code Exemption', 750, 'Student is allowed to spend one day\nwearing non-uniform clothing\n( 750 points )')")
    cursor.execute("INSERT INTO Token (token_id, token_name, point_cost, description) VALUES ( 2, 'Cafeteria coupon', 250, 'Student recieves 1 free meal\nfrom the school cafeteria\n( 250 points )')")
    cursor.execute("INSERT INTO Token (token_id, token_name, point_cost, description) VALUES ( 3, '1 day off', 1500, 'Student is allowed one day\nof registered abscence (provided that\ntheir teachers all allow it)\n( 1500 points )')")

    #Adding default values for tests
    cursor.execute("INSERT INTO Student (student_id, first_name, last_name, password, grade, house_id, total_points) VALUES (1899,'Arthur','Morgan','hosea', '13A', 1, 1000);")
    cursor.execute("INSERT INTO Student (student_id, first_name, last_name, password, grade, house_id, total_points) VALUES (1,'John','Doe','1', '13C', 2, 1500);")
    cursor.execute("INSERT INTO Teacher (teacher_id, first_name, last_name, password) VALUES (1, 'Walter', 'White', '1')")
    # cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (1899, 1, 0)")
    # cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (1899, 2, 0)")
    # cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (1899, 3, 0)")
    # cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (1, 1, 0)")
    # cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (1, 2, 0)")
    # cursor.execute("INSERT INTO Student_token_ownership (student_id, token_id, quantity) VALUES (1, 3, 0)")

    conn.commit()
    conn.close()

    #Note: If updating database,
    #do NOT
    #FORGET
    #TO RE-ADD
    #THE FUNCTION
    #!!!!!!!!!!!!!!!!!!!
