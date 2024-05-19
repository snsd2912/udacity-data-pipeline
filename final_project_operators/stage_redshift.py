from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook

from udacity.common.sql_statements import SqlQueries

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                    redshift_conn_id = "",
                    aws_credentials_id="",
                    table = "",
                    s3_path = "",
                    region = "",
                    json_path = "",
                    *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table           
        self.s3_path = s3_path
        self.region = region
        self.json_path = json_path
        self.execution_date = kwargs.get('execution_date')

    def execute(self, context):
        self.log.info('StageToRedshiftOperator implementation')
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Clearing data from destination Redshift table")
        redshift.run("DELETE FROM {}".format(self.table))

        self.log.info("Stage data from S3 to Redshift")
        formatted_sql = SqlQueries.staging_events_copy.format(
            self.table,
            self.s3_path,
            credentials.access_key,
            credentials.secret_key,
            self.json_path,
            self.region
        )

        redshift.run(formatted_sql)





