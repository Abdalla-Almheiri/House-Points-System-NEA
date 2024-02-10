        
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
            grade INTEGER,
            house_id INTEGER,
            total_points INTEGER,
            leaderboard_position INTEGER,
            PRIMARY KEY (student_id),
            FOREIGN KEY (house_id) REFERENCES House(house_id)
        );
    ''')

    #House_points_record table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS House_points_record (
            record_id INTEGER,
            student_id INTEGER,
            teacher_id INTEGER,
            points INTEGER,
            date_awarded DATETIME,
            PRIMARY KEY (record_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id)
        );
    ''')

    #Purchase_token table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Purchase_token (
            purchase_id INTEGER,
            student_id INTEGER,
            token_id INTEGER,
            purchase_date DATETIME,
            PRIMARY KEY (purchase_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (token_id) REFERENCES Token(token_id)
        );
    ''')

    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (1,'Gazelles');")
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (2,'Oryxes');")
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (3,'Foxes');")
    cursor.execute("INSERT INTO House (house_id, house_name) VALUES (4,'Falcons');")
    cursor.execute("INSERT INTO Student (student_id, first_name, last_name, password, grade, house_id, total_points) VALUES (1899,'Arthur','Morgan','hosea', 13, 1, 0);")

    conn.commit()
    conn.close()
