from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                    redshift_conn_id = "",
                    tests = [],
                    *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        
        self.redshift_conn_id = redshift_conn_id
        self.tests = tests

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)  
        
        self.log.info("==== Start data check ====")
        for test in self.tests:
            check_sql = test.get("check_sql")
            expected_result = test.get("expected_result")
            
            result = redshift.get_records(check_sql)[0]

            self.log.info("Query: {}".format(check_sql))
            self.log.info("Expected Result: {}".format(expected_result))
            self.log.info("Output: {}".format(result[0]))

            if result[0] == expected_result:
                self.log.info("Data quality check passed.")
            else:
                raise ValueError("Data quality check failed on query: {}".format(check_sql))
        
        self.log.info("==== End data check ====")
            