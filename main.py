from db_manager import DBManager
from hh_parser import HHParser

if __name__ == "__main__":
    config_path = 'db.ini'
    db_manager = DBManager(config_path=config_path)
    hh_parser = HHParser(db_manager)

    my_companies = {
                    1740: "Яндекс",
                    9498112: "Яндекс Крауд",
                    4244151: "Вдохновение",
                    9395611: "LiteJob",
                    5823323: "ФЛЕКСИКО",
                    2296035: "Агентство Очень Важный Персонал",
                    10059498: "CASABLANCA GROUP",
                    2771696: "АйТи Мегастар",
                    3089: "РУНА, консалтинговая группа",
                    3428160: "HardQode",
                    1060821: "Рост Развитие Решение",
                }

    hh_parser.parse_companies_and_vacancies(my_companies)

    companies_and_vacancies_count = db_manager.get_companies_and_vacancies_count()
    print("Companies and Vacancies Count:")
    print(companies_and_vacancies_count)

    all_vacancies = db_manager.get_all_vacancies()
    print("\nAll Vacancies:")
    print(all_vacancies)

    avg_salary = db_manager.get_avg_salary()
    print("\nAverage Salary:")
    print(avg_salary)

    vacancies_with_higher_salary = db_manager.get_vacancies_with_higher_salary()
    print("\nVacancies with Higher Salary:")
    print(vacancies_with_higher_salary)

    keyword = "python"
    vacancies_with_keyword = db_manager.get_vacancies_with_keyword(keyword)
    print(f"\nVacancies with keyword '{keyword}':")
    print(vacancies_with_keyword)

    db_manager.close_connection()
