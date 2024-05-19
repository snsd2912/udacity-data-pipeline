from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                    redshift_conn_id = "",
                    tables = [],
                    *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        
        self.redshift_conn_id = redshift_conn_id
        self.tables = tables

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)  
        
        for table in self.tables:
            records = redshift.get_records("SELECT COUNT(*) FROM {}".format(table))  
                
            row_count = records[0][0]
            if row_count == 0:
                raise ValueError("No records in table {}".format(table))
                
            self.log.info("Quality data check on table {} passed".format(table))
            