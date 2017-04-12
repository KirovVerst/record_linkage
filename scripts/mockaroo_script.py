import datetime, os
import pprint

from collections import defaultdict

from modules.dataset_receiving import Data
from modules.duplicate_searching import Predictor
from modules.result_estimation import get_differences
from modules.dataset_processing import EditDistanceMatrix
from modules.result_saving import Logger

try:
    from conf import BASE_DIR
except Exception as ex:
    from conf_example import BASE_DIR

INITIAL_DATA_SIZE = 100
DOCUMENT_NUMBER = 3
COLUMN_NAMES = ['first_name', 'last_name', 'father']
LEVELS = list(map(lambda x: [x / 100] * 3, range(67, 72)))
LIST_2_FLOAT = "sum"  # "norm", "sum"
RECORD_COMPARATOR = "and"  # "and", "or"


def func(document_index):
    current_time = datetime.datetime.now()
    print("Dataset {0} was started: \t\t{1}".format(document_index + 1, current_time))

    data_kwargs = {'init_data_size': INITIAL_DATA_SIZE, 'document_index': document_index}

    data = Data(dataset_type="mockaroo", kwargs=data_kwargs)

    matrix = EditDistanceMatrix(data.df, column_names=COLUMN_NAMES, concat=False, normalize="total")
    matrix_values = matrix.get()

    print("Matrix was calculated: \t\t{}".format(datetime.datetime.now()))

    results_grouped_by_level = dict()

    logger = Logger(FOLDER_PATH, dataset_index=document_index)

    predictor = Predictor(data=matrix_values['values'], levels=LEVELS,
                          list2float=LIST_2_FLOAT, comparator=RECORD_COMPARATOR, save_extra_data=True)

    predicted_duplicates = predictor.predict_duplicates()

    print("Duplicates were predicted: \t{}".format(datetime.datetime.now()))

    for duplicates in predicted_duplicates:
        errors = get_differences(data.true_duplicates['items'], duplicates['items'])
        errors['level'] = duplicates['level']
        errors['extra_data'] = duplicates['extra_data']
        level_str = str(errors['level'])
        results_grouped_by_level[level_str] = errors['number_of_errors']

        logger.save_errors(df=data.df, errors=errors)

        logger.save_duplicates(duplicates, errors['level'])

    time_delta = datetime.datetime.now() - current_time

    current_meta_data = {
        'dataset_size': len(data.df),
        'results': results_grouped_by_level,
        'time_delta': str(time_delta),
        'max_dist': str(matrix_values['max_dist']),
        'normalize': str(matrix.normalize),
        "concat": str(matrix.k == 1)
    }

    print("Dataset {0} is ready: \t\t{1}".format(document_index + 1, datetime.datetime.now()))
    print("Time delta: {0}".format(str(time_delta)))
    pprint.pprint(current_meta_data['results'])

    logger.save_data(data=current_meta_data)

    return results_grouped_by_level


if __name__ == "__main__":
    results = []
    START_TIME = datetime.datetime.now()
    START_TIME_STR = START_TIME.strftime("%d_%m_%H_%M_%S").replace(" ", "__")
    FOLDER_PATH = os.path.join(BASE_DIR, 'logs', '{0}_{1}'.format(START_TIME_STR, INITIAL_DATA_SIZE))

    total_time = datetime.timedelta()
    total_number_of_errors = 0
    total_result = defaultdict(int)
    for i in range(DOCUMENT_NUMBER):
        result = func(i)
        for level, value in result.items():
            total_result[level] += value

    print("-" * 80)

    for key in total_result:
        total_result[key] /= DOCUMENT_NUMBER

    meta_data = {
        "number_of_datasets": DOCUMENT_NUMBER,
        "init_dataset_size": INITIAL_DATA_SIZE,
        "dataset_fields": COLUMN_NAMES,
        "levels": LEVELS,
        "list2float_function": LIST_2_FLOAT,
        "record_comparision_function": RECORD_COMPARATOR,
        "average_number_of_errors": dict(total_result.items()),
        "total_time": str(datetime.datetime.now() - START_TIME),
    }
    pprint.pprint(meta_data)
    logger = Logger(FOLDER_PATH)
    logger.save_data(data=meta_data)
