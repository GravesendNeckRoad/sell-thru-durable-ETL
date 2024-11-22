from datetime import timedelta

from azure.durable_functions import DurableOrchestrationContext, Orchestrator


def main(context: DurableOrchestrationContext):
    """Compiles an on-hand report out of the prior activities (Orders_1-3, Inventory, ReportCompiler)"""
    account_name = context.get_input()

    # run sequentially, to avoid throttle
    orders1_result = yield context.call_activity('Activity_Order1', account_name)
    yield context.create_timer(context.current_utc_datetime + timedelta(seconds=3))
    
    orders2_result = yield context.call_activity('Activity_Order2', account_name)
    yield context.create_timer(context.current_utc_datetime + timedelta(seconds=3))

    orders3_result = yield context.call_activity('Activity_Order3', account_name)
    yield context.create_timer(context.current_utc_datetime + timedelta(seconds=3))

    inventory_result = yield context.call_activity('Activity_Inventory', account_name)
    yield context.create_timer(context.current_utc_datetime + timedelta(seconds=1))

    # pass dictionary of results to report compiler
    results = {
        'account_name': account_name,
        'orders': [orders1_result, orders2_result, orders3_result],
        'inventory': [inventory_result]
    }
    
    compiled_report = yield context.call_activity('Activity_ReportCompiler', results)
    return compiled_report  # returns a tuple with report name and the report itself, in json fmt


main = Orchestrator.create(main)
