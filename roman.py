from random import *
from math import *

int_dict = { 1 : "I", 5 : "V", 10 : "X", 50 : "L", 100 : "C", 500 : "D", 1000 : "M", 5000 : "V̄", 10000 : "X̄", 50000 : "L̄", 100000 : "C̄", 500000 : "D̄", 1000000 : "M̄"}
int_list = [1000000,500000,100000,50000,10000,5000,1000,500,100,50,10,5,1]
int_in = 0
string_out = ""


def roman_convert(int_in_string):
    global string_out
    global int_in
    string_out = ""
    int_in = int(int_in_string)
    if int_in >= 4000000:
        return "Please keep it less than 4,000,000, we don't know how to write 2 macrons."
    for poss_int in int_list:
        if str(poss_int)[0] == "1":
            addstring1(poss_int)
            addstring9(poss_int)
        else:
            addstring5(poss_int)
            addstring4(poss_int)
    return string_out        


def addstring1(num):
    global string_out
    global int_in
    while int_in >= num:
        string_out += int_dict[num]
        int_in = int_in - num 

def addstring4(num5):
    global string_out
    global int_in
    if int_in >= num5 * 4 / 5:
        string_out += int_dict[int(num5/5)] + int_dict[num5]
        int_in = int_in - (num5 * 4 / 5)

def addstring5(num5):
    global string_out
    global int_in
    if int_in >= num5:
        string_out += int_dict[num5]
        int_in = int_in - num5

def addstring9(num10):
    global string_out
    global int_in
    if num10 == 1:
        return
    if int_in >= num10 * 9 / 10:
        string_out += int_dict[int(num10/10)] + int_dict[num10]
        int_in = int_in - num10 * 9 / 10
        

def randbool():
    return (randint(0,1) == 1)