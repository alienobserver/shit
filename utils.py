import json
import pickle

ARM_MONTHS = {
        "հունվար":'01',
        "փետրվար":'02',
        "մարտ":'03',
        "ապրիլ":'04',
        "մայիս":'05',
        "հունիս":'06',
        "հուլիս":'07',
        "օգոստոս":'08',
        "սեպտեմբեր" : '09',
        "հոկտեմբեր":'10',
        "նոյեմբեր":'11',
        "դեկտեմբեր":'12'}



def read_data(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    return data
