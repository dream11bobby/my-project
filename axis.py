import pdfplumber
import tabula
from tabula.io import read_pdf
from Calculation import Calc
from transaction_category import fetch_transaction_category_from_data_base
import warnings
from calling_other_bsa_api import bsa_api
from formatting_the_data_to_dataframe import converting_list_to_data_frame

warnings.filterwarnings("ignore")

date: list = []
desc: list = []
chq_no: list = []
amount: list = []
balance: list = []
credit: list = []
debit: list = []
i: str = " "
j: str = "0"
df = None


def axis_bank(file_location, bank_name):
    global date, desc, chq_no, amount, balance, credit, debit, i, j, df
    date.clear()
    desc.clear()
    chq_no.clear()
    amount.clear()
    debit.clear()
    credit.clear()
    balance.clear()
    with pdfplumber.open(file_location) as pdf:
        table = tabula.read_pdf(file_location, pages="1", lattice=True)
        if ((table[0].shape[1] == 7) and (len(table) == 2)) or ((table[0].shape[1] == 16) and (len(table) == 1)):
            print("axis bank TYPE 1")
            try:
                for page in range(len(pdf.pages)):
                    try:
                        for trans in pdf.pages[page].extract_table():
                            if (len(str(trans[0]).split('-')) == 3) and (len(str(trans[-2]).split('.')) == 2):
                                date_format = Calc.identify_date_format(trans[0])
                                date.append(date_format)
                                desc.append(trans[2])
                                chq_no.append(trans[1])
                                credit.append(trans[-3])
                                debit.append(trans[-4])
                                processed_balance = Calc.finding_sign(trans[-2])
                                balance.append(processed_balance)
                    except Exception as Error:
                        print(f"The cause of error {Error}")
                        pass

                date_order = Calc.date_order(date)
                transaction_category = fetch_transaction_category_from_data_base(desc)
                dataframe, status = Calc.dataframe_for_box_type_pdf(date, desc, chq_no, debit, credit, balance,
                                                                    transaction_category, date_order)
            except Exception as Error:
                print(f"The cause of error {Error}")
                status = "Failed"
                return status, df

        elif (table[0].shape[1] == 8) and (len(table) == 1):
            print("axis bank TYPE 2")
            try:
                for page in range(len(pdf.pages)):
                    try:
                        for trans in pdf.pages[page].extract_table():
                            if len(str(trans[0]).split("-")) == 3:
                                date_format = Calc.identify_date_format(trans[0])
                                date.append(date_format)
                                desc.append(trans[2])
                                chq_no.append(trans[3])
                                if trans[-3] == "DR":
                                    debit.append(trans[-4])
                                else:
                                    debit.append(j)
                                if trans[-3] == "CR":
                                    credit.append(trans[-4])
                                else:
                                    credit.append(j)
                                processed_balance = Calc.finding_sign(trans[-2])
                                balance.append(processed_balance)
                    except Exception as Error:
                        print(f"The cause of error {Error}")
                        pass

                date_order = Calc.date_order(date)
                transaction_category = fetch_transaction_category_from_data_base(desc)
                dataframe, status = Calc.dataframe_for_box_type_pdf(date, desc, chq_no, debit, credit, balance,
                                                                    transaction_category, date_order)
            except Exception as Error:
                print(f"The cause of error {Error}")
                status = "Failed"
                return status, df

        elif (table[0].shape[1] == 8) and (len(table) == 2):
            print("axis bank TYPE 3")
            try:
                for page in range(len(pdf.pages)):
                    try:
                        for trans in pdf.pages[page].extract_table():
                            if len(str(trans[0]).split("-")) == 3:
                                date_format = Calc.identify_date_format(trans[0])
                                date.append(date_format)
                                desc.append(trans[2])
                                chq_no.append(i)
                                if trans[-3] == "DR":
                                    debit.append(trans[-4])
                                else:
                                    debit.append(j)
                                if trans[-3] == "CR":
                                    credit.append(trans[-4])
                                else:
                                    credit.append(j)
                                processed_balance = Calc.finding_sign(trans[-2])
                                balance.append(processed_balance)

                    except Exception as Error:
                        print(f"The cause of error {Error}")
                        pass

                if debit[0] == "0" and credit[0] == "0":
                    dataframe, status = axis_bank_other_type(file_location)
                else:
                    date_order = Calc.date_order(date)
                    transaction_category = fetch_transaction_category_from_data_base(desc)
                    dataframe, status = Calc.dataframe_for_box_type_pdf(date, desc, chq_no, debit, credit, balance,
                                                                                    transaction_category, date_order)
            except Exception as Error:
                print(f"The cause of error {Error}")
                status = "Failed"
                return status, df

        else:
            print("[CALLING BSA API ...]")
            status_code, response_data = bsa_api(bank_name, file_location)
            if status_code == "success":
                dataframe, status = converting_list_to_data_frame(response_data)
                return status, dataframe
            else:
                status_code = "failed"
                return status_code, df

        if status == "success":
            return status, dataframe
        else:
            print("[CALLING BSA API ...]")
            status_code, response_data = bsa_api(bank_name, file_location)
            if status_code == "success":
                dataframe, status = converting_list_to_data_frame(response_data)
                return status, dataframe
            else:
                status_code = "failed"
                return status_code, df

def axis_bank_other_type(file_location):
    print("Entering to axis other type")
    global date, desc, chq_no, amount, balance, credit, debit, i, j, df
    date.clear()
    desc.clear()
    chq_no.clear()
    debit.clear()
    credit.clear()
    balance.clear()
    with pdfplumber.open(file_location) as pdf:
        table = tabula.read_pdf(file_location, pages="1", lattice=True)
        if (table[0].shape[1] == 8) and (len(table) == 2):
            print("axis bank TYPE 3.1")
            try:
                for page in range(len(pdf.pages)):
                    try:
                        for trans in pdf.pages[page].extract_table():
                            if len(str(trans[0]).split("-")) == 3:
                                date_format = Calc.identify_date_format(trans[0])
                                date.append(date_format)
                                desc.append(trans[2])
                                chq_no.append(i)
                                if trans[-4] == "":
                                    debit.append(j)
                                else:
                                    debit.append(trans[-4])
                                if trans[-3] == "":
                                    credit.append(j)
                                else:
                                    credit.append(trans[-3])
                                processed_balance = Calc.finding_sign(trans[-2])
                                balance.append(processed_balance)

                    except Exception as Error:
                        print(f"The cause of error {Error}")
                        pass

                date_order = Calc.date_order(date)
                transaction_category = fetch_transaction_category_from_data_base(desc)
                dataframe, status = Calc.dataframe_for_box_type_pdf(date, desc, chq_no, debit, credit, balance,
                                                                    transaction_category, date_order)
            except Exception as Error:
                print(f"The cause of error {Error}")
                status = "Failed"

            return dataframe, status
