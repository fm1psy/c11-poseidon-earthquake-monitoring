# pylint: disable=W0718, W1203

"""Main file to run the entire ETL process"""

import logging
from extract import extract_process
from transform import transform_process
from load import load_process


def run_pipeline():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    logging.info('Starting pipeline')

    try:
        extracted_data = extract_process()
    except Exception as e:
        logging.error(f'Error during extraction: {e}')

    try:
        transformed_data = transform_process(extracted_data)
    except Exception as e:
        logging.error(f'Error during transform: {e}')

    try:
        load_process(transformed_data)
        logging.info('Pipeline completed running')
    except Exception as e:
        logging.error(f'Error during load: {e}')


if __name__ == "__main__":
    run_pipeline()
