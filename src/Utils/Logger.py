import logging
logging.basicConfig(filename='src/Data/user_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_activity(message):
    logging.info(message)

if __name__ == "__main__":
    log_activity("hiiiiiiiiii_testinggggggggggg")