#!/usr/bin/python3
# Name: main.py
# Date: Nov 01, 2022
#
# Please, before you run this script make sure you have spacy lib and en_core_web_sm installed
# You can either run the "deps.py" script or install it manually with the following procedure
# 1: python3 -m pip install spacy==3.4.2
# 2: python3 -m spacy download en_core_web_sm

import argparse
import locale
import re
import spacy
import sys

locale.setlocale(locale.LC_ALL, "")


class Person:
    def __init__(self, email: str) -> None:
        self.__email: str = self.__validate_email(email)
        self.__companies: set = set()
        self.__investments: list = []
        self.__amount_invested: float = 0.0
        self.__investments_per_company: list[dict[str, float]] = []

    def __validate_email(self, email: str) -> str:
        regex: re.Pattern[str] = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

        if not re.fullmatch(regex, email):
            raise Exception(f"email does not match regex: {regex}")

        return email

    def __generate_investments_per_company(self) -> None:
        for index, company in enumerate(self.__companies):
            investment_per_company_obj: dict[str, float] = {
                "company": company,
                "investment": float(self.__investments[index])
            }

            self.__investments_per_company.append(investment_per_company_obj)

    @property
    def email(self):
        return self.__email

    @property
    def companies(self) -> set:
        return self.__companies

    @companies.setter
    def companies(self, companies: set):
        self.__companies: set = companies

    @property
    def investments(self) -> list:
        return self.__investments

    @investments.setter
    def investments(self, values_list: list):
        for value in values_list:
            just_value = re.search(r"(?!,$)[\d,.]+", value).group()
            new_value = just_value if "," not in just_value else just_value.replace(",", "")

            for conv in Converters.number_converters():
                for k, v in conv.items():
                    if k in value.lower():
                        new_value = float(just_value) * float(v)

            self.__investments.append(float(new_value))
            self.__amount_invested += float(new_value)

    @property
    def amount_invested(self):
        return self.__amount_invested

    def print_person(self, padding: int):
        self.__generate_investments_per_company()

        sentence = f"{self.__email}:".ljust(padding) + f"{locale.currency(self.__amount_invested, grouping=True)} to"

        for index, company in enumerate(self.__companies):
            if index > 0 and index < (len(self.__companies) - 1):
                sentence += f", {company}"
            elif index > 0 and index == (len(self.__companies) - 1):
                sentence += f" and {company}"
            else:
                sentence += f" {company}"

        sentence += "."

        if len(self.__investments_per_company) > 1:
            for index, investment_per_company in enumerate(self.__investments_per_company):
                if index > 0 and index < (len(self.__companies) - 1):
                    sentence += f", {locale.currency(investment_per_company['investment'], grouping=True)} to {investment_per_company['company']}"
                elif index > 0 and index == (len(self.__companies) - 1):
                    sentence += f" and {locale.currency(investment_per_company['investment'], grouping=True)} to {investment_per_company['company']}"
                else:
                    sentence += f" {locale.currency(investment_per_company['investment'], grouping=True)} to {investment_per_company['company']}"

            sentence += "."

        print(sentence)


class Converters:
    def __init__(self):
        pass

    @staticmethod
    def number_converters() -> list:
        return [
            {"zero": 0},
            {"one": 1},
            {"two": 2},
            {"three": 3},
            {"four": 4},
            {"five": 5},
            {"six": 6},
            {"seven": 7},
            {"eight": 8},
            {"nine": 9},
            {"ten": 10},
            {"twenty": 20},
            {"thirty": 30},
            {"forty": 40},
            {"fifty": 50},
            {"sixty": 60},
            {"seventy": 70},
            {"eighty": 80},
            {"ninety": 90},
            {"hundred": 100},
            {"thousand": 1000},
            {"million": 1000000},
            {"billion": 1000000000},
            {"trillion": 1000000000000},
            {"quadrillion": 1000000000000000}
        ]


def create_email_log_object_list(email_log_list: list) -> list:
    if not isinstance(email_log_list, list):
        raise Exception(f"{email_log_list} of type {type(email_log_list)} is not a list")

    email_log_object_list = []

    for email_log in email_log_list:
        parts = email_log.split("\n")

        email_log_object_list.append({
            "email": parts[0],
            "emailLen": len(parts[0]),
            "message": "".join(parts[1:])
        })

    return email_log_object_list


def parse_email_log(filename: str) -> list:
    email_log_list = []

    with open(file=filename, mode="r", encoding="utf-8") as email_log:
        data_list = email_log.read().split("<<End>>")

        for data in data_list:
            if data != "\n":
                data = data.rstrip("\n").lstrip("\n")

                email_log_list.append(data)

    return create_email_log_object_list(email_log_list)


def print_to_console(people_list: list, padding: int):
    total_amount = 0.0

    for person in people_list:
        person.print_person(padding)

        total_amount += person.amount_invested

    print("Total Requests:".ljust(padding) + f"{locale.currency(total_amount, grouping=True)}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--filename", help="email log file")

    args = parser.parse_args()

    filename = args.filename if len(sys.argv) == 3 else "./EmailLog.txt"

    nlp = spacy.load("en_core_web_sm")

    data_list = parse_email_log(filename)

    people_list = []
    max_email_len = 0

    for data in data_list:
        email = data["email"]
        email_len = data["emailLen"]
        message = data["message"]

        if email_len > max_email_len:
            max_email_len = email_len

        p = Person(email)

        doc = nlp(message)

        investments_list = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]

        p.investments = investments_list

        companies_list = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        p.companies = companies_list

        people_list.append(p)

    print_to_console(people_list, max_email_len + 2)


if __name__ == "__main__":
    main()
