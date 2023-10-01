import requests

class HHParser:
    HH_API_URL = 'https://api.hh.ru'

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_company_info(self, hh_id):
        response = requests.get(f'{self.HH_API_URL}/employers/{hh_id}')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get company info for hh_id {hh_id}. Status code: {response.status_code}")
            return None

    def get_company_vacancies(self, hh_id):
        response = requests.get(f'{self.HH_API_URL}/vacancies', params={'employer_id': hh_id})
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"Failed to get vacancies for company with hh_id {hh_id}. Status code: {response.status_code}")
            return []

    def parse_companies_and_vacancies(self, companies):
        for hh_id, name in companies.items():
            try:
                # Получаем информацию о компании
                company_info = self.get_company_info(hh_id)

                if company_info is not None:
                    # Вставляем информацию о компании в базу данных
                    self.db_manager.insert_company(hh_id, name)

                    # Получаем вакансии компании
                    vacancies = self.get_company_vacancies(hh_id)
                    vacancies_count = len(vacancies)

                    # Выводим информацию в консоль
                    print(f"Company: {name}, Vacancies Count: {vacancies_count}")

                    if vacancies_count > 0:
                        for vacancy in vacancies:
                            # Проверяем наличие опыта и зарплаты
                            if vacancy.get('experience') and vacancy.get('salary') and \
                                    (vacancy['salary'].get('from') or vacancy['salary'].get('to')):
                                print("\nVacancy:")
                                print(f"Title: {vacancy.get('name')}")
                                print(f"Link: {vacancy.get('alternate_url')}")
                                print(f"Salary: {vacancy['salary'].get('from')} - {vacancy['salary'].get('to')} {vacancy['salary'].get('currency')}")
                                print(f"Type of work: {vacancy['employment'].get('name')}")
                                print(f"Experience: {vacancy['experience'].get('name')}")
                                print("------------------------")

                                # Вставляем информацию о вакансии в базу данных
                                parsed_vacancy = {
                                    "employer_id": hh_id,
                                    "title": vacancy.get('name'),
                                    "client": name,
                                    "salary_from": vacancy['salary'].get('from'),
                                    "salary_to": vacancy['salary'].get('to'),
                                    "currency": vacancy['salary'].get('currency'),
                                    "type_of_work": vacancy['employment'].get('name'),
                                    "experience": vacancy['experience'].get('name'),
                                    "link": vacancy.get('alternate_url'),
                                }
                                self.db_manager.insert_vacancy(parsed_vacancy)

                        # Сохраняем изменения в базе данных
                        self.db_manager.commit()

                else:
                    print(f"Company info not found for hh_id {hh_id}")

            except Exception as e:
                print(f"Error processing company with hh_id {hh_id}: {str(e)}")
