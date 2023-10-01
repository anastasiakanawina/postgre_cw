import psycopg2
import configparser


class DBManager:
    def __init__(self, config_path='db.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        dbname = config['postgresql']['dbname']
        user = config['postgresql']['user']
        password = config['postgresql']['password']
        host = config['postgresql']['host']
        port = config['postgresql']['port']

        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                hh_id INTEGER UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                employer_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                client VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                type_of_work VARCHAR(50) NOT NULL,
                experience VARCHAR(50) NOT NULL,
                link VARCHAR(255) NOT NULL
            )
        ''')

        self.conn.commit()

    def insert_company(self, hh_id, name):
        self.cursor.execute('''
            INSERT INTO companies (hh_id, name) VALUES (%s, %s)
            ON CONFLICT (hh_id) DO NOTHING
        ''', (hh_id, name))
        self.conn.commit()

    def insert_vacancy(self, parsed_vacancy):
        self.cursor.execute('''
            INSERT INTO companies (hh_id, name) VALUES (%s, %s)
            ON CONFLICT (hh_id) DO NOTHING
        ''', (parsed_vacancy['employer_id'], parsed_vacancy['client']))

        self.cursor.execute('''
            INSERT INTO vacancies (
                employer_id, title, client, salary_from, salary_to, currency,
                type_of_work, experience, link
            ) VALUES (
                (SELECT id FROM companies WHERE hh_id = %s),
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        ''', (
            parsed_vacancy['employer_id'], parsed_vacancy['title'], parsed_vacancy['client'],
            parsed_vacancy['salary_from'], parsed_vacancy['salary_to'], parsed_vacancy['currency'],
            parsed_vacancy['type_of_work'], parsed_vacancy['experience'], parsed_vacancy['link']
        ))
        self.conn.commit()

    def get_companies_and_vacancies_count(self):
        self.cursor.execute('''
            SELECT c.name, COUNT(v.id) as vacancy_count
            FROM companies c
            LEFT JOIN vacancies v ON c.id = v.employer_id
            GROUP BY c.name
        ''')
        result = self.cursor.fetchall()
        return result

    def get_all_vacancies(self):
        self.cursor.execute('''
            SELECT c.name as company_name, v.title, v.salary_from, v.salary_to, v.currency, v.link
            FROM vacancies v
            JOIN companies c ON c.id = v.employer_id
        ''')
        result = self.cursor.fetchall()
        return result

    def get_avg_salary(self):
        self.cursor.execute('''
            SELECT AVG(salary_from) as avg_salary
            FROM vacancies
        ''')
        result = self.cursor.fetchone()
        return result[0]

    def get_vacancies_with_higher_salary(self):
        avg_salary = self.get_avg_salary()
        self.cursor.execute('''
            SELECT title, salary_from, salary_to, currency, link
            FROM vacancies
            WHERE salary_from > %s
            OR salary_to > %s
        ''', (avg_salary, avg_salary))
        result = self.cursor.fetchall()
        return result

    def get_vacancies_with_keyword(self, keyword):
        self.cursor.execute('''
            SELECT title, salary_from, salary_to, currency, link
            FROM vacancies
            WHERE title ILIKE %s
        ''', (f"%{keyword}%",))
        result = self.cursor.fetchall()
        return result

    def commit(self):
        self.conn.commit()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
