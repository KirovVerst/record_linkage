import pandas as pd
from qlink.indexation import Indexation
from qlink.matrix_calculation import MatrixCalculation

from examples.conf import MIAC_SMALL_DATA, MIAC_STR_FIELDS, MIAC_DATE_FIELDS
from qlink.duplicate_searching import Searcher


def run(is_sample, size=None):
    dataframe = pd.read_csv(MIAC_SMALL_DATA['full']['data'], index_col='id')
    folder = MIAC_SMALL_DATA['full']

    if is_sample:
        if size is None:
            size = 1000
        dataframe = dataframe[:size]
        dataframe.to_csv(MIAC_SMALL_DATA['sample']['data'], index=True)
        folder = MIAC_SMALL_DATA['sample']

    dataframe.fillna(value='', inplace=True)

    mode = 'letters'

    indexator = Indexation(dataframe=dataframe,
                           index_field='last_name',
                           mode=mode,
                           index_output_path=folder['index-letters'])
    indexator.create_index_dict(njobs=-1)

    matrix_calculator = MatrixCalculation(dataframe=dataframe,
                                          index_path=folder['index-letters'],
                                          matrix_path=folder['matrix'],
                                          index_field='last_name',
                                          norm_matrix_path=folder['norm-matrix'],
                                          str_fields=MIAC_STR_FIELDS,
                                          date_fields=MIAC_DATE_FIELDS)
    matrix_calculator.create_matrix(njobs=-1)

    searcher = Searcher(dataframe=dataframe,
                        norm_matrix_path=folder['norm-matrix'],
                        duplicates_path=folder['duplicates'],
                        mode='all')
    searcher.search_duplicates([[0.8, 0.8, 0.8, 0.9]])


def search(is_sample):
    folder = MIAC_SMALL_DATA['sample'] if is_sample else MIAC_SMALL_DATA['full']
    dataframe = pd.read_csv(folder['data'], index_col='id')
    searcher = Searcher(dataframe=dataframe,
                        norm_matrix_path=folder['norm-matrix'],
                        duplicates_path=folder['duplicates'],
                        mode='all')
    searcher.search_duplicates([[0.8, 0.8, 0.8, 0.9]])


if __name__ == '__main__':
    run(is_sample=True)
