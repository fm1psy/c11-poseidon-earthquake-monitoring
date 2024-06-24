"""Lambda Handler"""

import traceback
from os import environ as ENV
from dotenv import load_dotenv
import main


def handler(event=None, context=None) -> dict:  # pylint: disable=unused-argument
    """
    Handler function required for lambda
    """
    try:
        load_dotenv()
        num_plants = int(ENV["NUM_PLANTS"])
        main.run_pipeline(num_plants)

        return {
            'status': 'Pipeline ran successfully'
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            'status': 'Pipeline running stopped',
            'reason': str(e),
            'stack_trace': traceback.format_exc()
        }


if __name__ == "__main__":
    print(handler())
