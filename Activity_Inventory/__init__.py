import logging
from Utilities.report_tools import ReportDownloadOrchestrator
from Utilities.utils import Helpers


def main(name: str) -> str:
    """Generates current in-stock inventory report, returned as json string"""

    compile = ReportDownloadOrchestrator(account_name=name)
    help = Helpers()

    logging.info(f"Generating inventory 1/1 report for acc '{name}'")
       
    current_attempt = 1
    max_attempts = 3
    while current_attempt <= max_attempts:        
        try: 
            data = compile.get_report(
                report_type='GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA',
                start_date=None,
                end_date=None
            )
            return data 
        
        except Exception as e:

            if current_attempt > max_attempts:
                logging.error(f"Max retry attempts reached on inventory #1 for '{name}'")
                raise Exception(f"Failed to generate inventory report for acc '{name}' after {max_attempts} retries")

            logging.error(f"Error on attempt #{current_attempt} for acc '{name}': {str(e)}")
            help.exponential_backoff(n=current_attempt, base_seconds=5, rate_of_growth=1.75)
            current_attempt += 1
            
    