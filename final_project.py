from datetime import datetime, timedelta
import pendulum
import os
from airflow.decorators import dag
from airflow.operators.dummy_operator import DummyOperator
from final_project_operators.stage_redshift import StageToRedshiftOperator
from final_project_operators.load_fact import LoadFactOperator
from final_project_operators.load_dimension import LoadDimensionOperator
from final_project_operators.data_quality import DataQualityOperator
from udacity.common.sql_statements import SqlQueries
from airflow.operators.postgres_operator import PostgresOperator

default_args = {
    "owner": 'udacity',
    "depends_on_past": False,
    "start_date": pendulum.now(),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
    "email_on_retry": False,
}

@dag(
    default_args=default_args,
    description='Load and transform data in Redshift with Airflow',
    schedule_interval='@hourly'
)
def final_project():

    start_operator = DummyOperator(task_id='Begin_execution')

    stage_events_to_redshift = StageToRedshiftOperator(
        task_id='Stage_events',
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        table="staging_events",
        s3_path='s3://udacity-dend/log_data',
        region='us-west-2',
        json_path="s3://udacity-dend/log_json_path.json",
    )

    stage_songs_to_redshift = StageToRedshiftOperator(
        task_id='Stage_songs',
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        table="staging_songs",
        s3_path='s3://udacity-dend/song_data',
        region='us-west-2',
        json_path="auto",
    )

    load_songplays_table = LoadFactOperator(
        task_id='Load_songplays_fact_table',
        redshift_conn_id="redshift",
        table="songplays",
        sql=SqlQueries.songplay_table_insert,
    )

    load_user_dimension_table = LoadDimensionOperator(
        task_id='Load_user_dim_table',
        redshift_conn_id="redshift",
        table="users",
        sql=SqlQueries.user_table_insert,
    )

    load_song_dimension_table = LoadDimensionOperator(
        task_id='Load_song_dim_table',
        redshift_conn_id="redshift",
        table="songs",
        sql=SqlQueries.song_table_insert,
    )

    load_artist_dimension_table = LoadDimensionOperator(
        task_id='Load_artist_dim_table',
        redshift_conn_id="redshift",
        table="artists",
        sql=SqlQueries.artist_table_insert,
    )

    load_time_dimension_table = LoadDimensionOperator(
        task_id='Load_time_dim_table',
        redshift_conn_id="redshift",
        table="time",
        sql=SqlQueries.time_table_insert,
    )

    run_quality_checks = DataQualityOperator(
        task_id='Run_data_quality_checks',
        redshift_conn_id="redshift",
        tests=[
            {
                "check_sql": "SELECT COUNT(*) FROM users WHERE userid is null",
                "expected_result": 0,
            },
            {
                "check_sql": "SELECT COUNT(*) FROM songs WHERE songid is null",
                "expected_result": 0,
            },
        ],
    )

    end_operator = DummyOperator(task_id='Stop_execution')

    start_operator  \
        >> [stage_events_to_redshift, stage_songs_to_redshift] \
        >> load_songplays_table \
        >> [ load_user_dimension_table, load_song_dimension_table, load_artist_dimension_table, load_time_dimension_table] \
        >> run_quality_checks \
        >> end_operator

final_project_dag = final_project()
