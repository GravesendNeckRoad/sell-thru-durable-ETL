import logging

from azure.durable_functions import DurableOrchestrationContext, Orchestrator, RetryOptions

from Utilities.report_tools import GenerateFBAReport


def main(context: DurableOrchestrationContext):
    """
    Generates 'on-hand' .xlsx reports for your Amazon account(s) by fetching data from SP-API

    -Main orchestrator: Runs Generator for account(s) in parallel, and compiles with Assembler         
    -SubOrchestrator_Generator: sequentially runs Activities Order1-3, Inventory, and ReportCompiler
    -SubOrchestrator_Assembler: Assembles the report created by Generator, and uploads to blob account
    """       
    # define a catch-all retry policy in case any of the API activities fail 
    retry_options = RetryOptions(
        first_retry_interval_in_milliseconds=(300),
        max_number_of_attempts=3
    )
    
    try:
        # fetch list of accounts to run reports for
        fetcher = GenerateFBAReport()
        accounts_list = fetcher.current_accounts
        
        # run sub-orchestrators in parallel for each account
        parallel_tasks = []
        for account in accounts_list:
            task = context.call_sub_orchestrator_with_retry('SubOrchestrator_Generator', retry_options, account)
            parallel_tasks.append(task) 
            
        results = yield context.task_all(parallel_tasks)
        
        # assemble to final report, format, and upload to blob
        yield context.call_sub_orchestrator('SubOrchestrator_Assembler', results)

        # exit explicitly to avoid unwanted restarts 
        context.set_custom_status("Completed")
        return None
    
    # fall back to retry options if anything goes awry 
    except Exception as e:
        logging.error(f"Main orchestrator failure: {str(e)}")
        context.set_custom_status("Failed")
        raise 

main = Orchestrator.create(main)
