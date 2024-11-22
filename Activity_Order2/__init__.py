import logging
from Utilities.report_tools import ReportDownloadOrchestrator
from Utilities.utils import Helpers


def main(name: str) -> str:
    """Generates orders report for orders between 30 and 60 days ago, returned as json string"""

    compile = ReportDownloadOrchestrator(account_name=name)
    help = Helpers()

    logging.info(
        f"Generating orders report 2/3 for acc '{name}' for range {compile.two_months_ago} - {compile.one_month_ago}"
        )
       
    current_attempt = 1
    max_attempts = 3
    while current_attempt <= max_attempts:        
        try: 
            data = compile.get_report(
                report_type='GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL',
                start_date=compile.two_months_ago,
                end_date=compile.one_month_ago
            )
            return data 
        
        except Exception as e:

            if current_attempt > max_attempts:
                logging.error(f"Max retry attempts reached on orders #2 for '{name}'")
                raise Exception(f"Failed to generate report #2 for acc '{name}' after {max_attempts} retries")

            logging.error(f"Error on attempt #{current_attempt} for acc '{name}': {str(e)}")
            help.exponential_backoff(n=current_attempt, base_seconds=5, rate_of_growth=1.75)
            current_attempt += 1
            
    