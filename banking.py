# Write your code here
import random
import math
import sqlite3
from sys import exit


class Bank:
    welcome_menu = '1. Create an account\n2. Log into account\n0. Exit'
    logged_in_menu = '1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit'
    bin = '400000'
    card_db = 'card.s3db'
    connection_to_db = sqlite3.connect(card_db)
    cur = connection_to_db.cursor()
    create_card_table = """CREATE TABLE IF NOT EXISTS card 
                        (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);"""
    current_card_number = ''
    current_card_balance = ''
    card_to_transfer = ''
    card_to_transfer_balance = ''

    def test(self):
        self.cur.execute('SELECT * FROM card')
        result = self.cur.fetchall()
        self.connection_to_db.commit()
        print(result)

    @staticmethod
    def account_identifier_generator():
        return str(random.randint(100000000, 999999999))

    @staticmethod
    def luhn_algorithm(card_num):
        control_number = 0
        luhn_card_number = [int(e) for e in card_num]
        # mulitiply odd nums by 2
        for i, val in enumerate(luhn_card_number):
            if i % 2 == 0:
                luhn_card_number[i] *= 2
        # substract 9 to nums over 9
        for i, val in enumerate(luhn_card_number):
            if val > 9:
                luhn_card_number[i] -= 9
        # sum of all nums
        for val in luhn_card_number:
            control_number += val
        if control_number % 10 == 0:
            return '0'
        else:
            return str(int(math.ceil(control_number / 10.0)) * 10 - control_number)

    def card_number_generator(self):
        base_card_number = [self.bin, Bank.account_identifier_generator()]
        check_sum = Bank.luhn_algorithm(''.join(base_card_number))
        final_card_number = [''.join(base_card_number), check_sum]
        return ''.join(final_card_number)

    @staticmethod
    def pin_generator():
        pin_def_list = ''
        for i in range(1, 5):
            pin_def_list += str(random.randint(0, 9))
            i += 1
        return ''.join(pin_def_list)

    def create_account(self):
        random.seed()
        card_number = self.card_number_generator()
        pin = Bank.pin_generator()
        print('Your card has been created\nYour card number:')
        print(card_number)
        print('Your card PIN:')
        print(pin)
        try:
            self.cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_number, pin))
        except Exception as e:
            print(e)
        self.connection_to_db.commit()
        return

    def input_balance(self):
        getting_balance_from_db = 'SELECT balance FROM card WHERE number=:card_number'
        self.cur.execute(getting_balance_from_db, {"card_number": self.current_card_number})
        balance = self.cur.fetchone()
        self.connection_to_db.commit()
        return balance

    def check_if_card_to_transfer_exists(self):
        check_card_existing = 'SELECT * FROM card WHERE number=:card_number'
        self.cur.execute(check_card_existing, {"card_number": self.card_to_transfer})
        card_exist = self.cur.fetchone()
        self.connection_to_db.commit()
        return card_exist

    def check_card_to_transfer(self):
        if list(self.card_to_transfer)[-1] != Bank.luhn_algorithm(''.join(list(self.card_to_transfer)[0:-1])):
            print('Probably you made a mistake in the card number. Please try again!')
            self.connection_to_db.commit()
        elif not self.check_if_card_to_transfer_exists():
            print('Such a card does not exist.')
        elif self.card_to_transfer == self.current_card_number:
            print('You can\'t transfer money to the same account!')
        else:
            return True
        return

    def get_current_balance_for_transfer(self):
        current_balance_for_transfer = 'SELECT balance FROM card WHERE number=:card_number'
        self.cur.execute(current_balance_for_transfer, {"card_number": self.card_to_transfer})
        balance_for_transfer = self.cur.fetchone()
        self.connection_to_db.commit()
        return balance_for_transfer

    def do_transfer(self):
        print('Transfer\nEnter card number:')
        self.card_to_transfer = input()
        if self.check_card_to_transfer():
            self.card_to_transfer_balance = self.get_current_balance_for_transfer()[0]
            self.connection_to_db.commit()
            print('Enter how much money you want to transfer:')
            sum_to_transfer = int(input())
            if sum_to_transfer <= self.current_card_balance:
                self.card_to_transfer_balance += sum_to_transfer
                incoming = 'UPDATE card SET balance=:balance WHERE number=:card_number'
                self.cur.execute(incoming, {"balance": self.card_to_transfer_balance, "card_number": self.card_to_transfer})
                self.connection_to_db.commit()
                self.current_card_balance -= sum_to_transfer
                transfering = 'UPDATE card SET balance=:balance WHERE number=:card_number'
                self.cur.execute(transfering, {"balance": self.current_card_balance, "card_number": self.current_card_number})
                self.connection_to_db.commit()
                print('Success!')
            else:
                print('Not enough money!')
        return

    def do_add_income(self):
        print('Enter income:')
        sum_to_income = int(input())
        self.current_card_balance += sum_to_income
        adding_income = 'UPDATE card SET balance=:balance WHERE number=:card_number'
        self.cur.execute(adding_income, {"balance": self.current_card_balance, "card_number": self.current_card_number})
        self.connection_to_db.commit()
        print('Income was added!')

    def close_account(self):
        account_closing = 'DELETE FROM card WHERE number=:card_number'
        self.cur.execute(account_closing, {"card_number": self.current_card_number})
        self.connection_to_db.commit()
        # self.test()
        print('The account has been closed!')

    def action_logged_in(self):
        while True:
            print(self.logged_in_menu)
            select_action = input()
            if select_action == '1':  # Balance
                print('Balance: ', self.current_card_balance)
            elif select_action == '2':   # Add income
                self.do_add_income()
            elif select_action == '3':   # Do transfer
                self.do_transfer()
            elif select_action == '4':   # Close account
                self.close_account()
                break
            elif select_action == '5':   # Log out - ready
                print('You have successfully logged out!')
                break
            elif select_action == '0':   # Exit
                print('Bye!')
                exit()
        return

    def login(self):
        print('Enter your card number:')
        self.current_card_number = input()
        getting_pin_from_db = 'SELECT pin FROM card WHERE number=:card_number'
        self.cur.execute(getting_pin_from_db, {"card_number": self.current_card_number})
        pin_from_db = self.cur.fetchone()
        self.connection_to_db.commit()
        print('Enter your PIN:')
        current_pin = input()
        try:
            if pin_from_db and pin_from_db[0] == current_pin:
                print('You have successfully logged in!')
                try:
                    self.current_card_balance = self.input_balance()[0]
                    self.connection_to_db.commit()
                except Exception as e:
                    print(e)
                self.action_logged_in()
            else:
                print('Wrong card number or PIN!')
        except sqlite3.Error as er:
            print(er)
            print('Wrong card number or PIN!')
        return

    def check_if_db_exists(self):
        return sqlite3.connect(self.card_db)

    def connect_to_db(self):
        try:
            self.check_if_db_exists()
        except sqlite3.OperationalError:
            self.cur.execute('CREATE DATABASE card')
            self.connection_to_db.commit()
        return

    def __init__(self):
        self.connect_to_db()
        # self.cur.execute('DROP TABLE card;')
        account_closing = 'DELETE FROM card WHERE number = "4000003305160035"'
        self.cur.execute(account_closing)
        self.connection_to_db.commit()
        self.cur.execute(self.create_card_table)
        self.connection_to_db.commit()
        # self.test()
        while True:
            print(self.welcome_menu)
            choose_action = input()
            if choose_action == '1':
                self.create_account()
            elif choose_action == '2':
                self.login()
            elif choose_action == '0':
                print('Bye!')
                exit()


my_account = Bank()
