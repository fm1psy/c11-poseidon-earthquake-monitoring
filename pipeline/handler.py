"""Lambda Handler"""

import traceback
from main import run_pipeline


def handler(event=None, context=None) -> dict:  # pylint: disable=unused-argument
    """
    Handler function required for lambda
    """
    try:
        run_pipeline()

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
