### audit.py
# The purpose of this script is to generate a csv of meta data for all jobs in a Domino project 
###

### Imports
from packages import *
from classes import *
from functions import *


### Vars and log settings
# I'd like to move more of these values into the report_config.ini file. 
config = configparser.ConfigParser()
config.read('report_config.ini')

project_name = os.getenv('DOMINO_PROJECT_NAME')
project_id = os.getenv('DOMINO_PROJECT_ID')
api_host = os.getenv('DOMINO_API_HOST')
api_key = os.getenv('DOMINO_USER_API_KEY')

columns_to_expand = ['stageTime', 'startedBy', 'commitDetails', 'statuses', 'environment', 'startState', 'endState']
columns_to_datetime = ['stageTime-submissionTime', 'stageTime-runStartTime', 'stageTime-completedTime']
column_order = config['column_order']

output_location = '/mnt/artifacts'




logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info(f"Generating audit report for {project_name}...")

domino = Domino(
    api_host = api_host,
    api_key = api_key
)


### starting timer
t0 = datetime.datetime.now()

### get list of jobs and goals in current project
logging.info("Generating list of project IDs for report...")
job_ids = get_jobs(domino, project_id)
goals = get_goals(domino, project_id)
logging.info(f"Found {len(job_ids)} jobs to report. Aggregating job metadata...")

### extract available metadata from each job 
try:
    logging.info(f"Attempting parallelized API queries...")
    t = datetime.datetime.now()
    jobs_raw = aggregate_job_data(domino, job_ids, parallelize=True)
    t = datetime.datetime.now() - t 
    logging.info(f"Queries succeeded in {str(round(t.total_seconds(),1))} seconds.")
except:
    logging.info(f"Parallel queries failed, attempting single-threaded API queries...")
    t = datetime.datetime.now()
    jobs_raw = aggregate_job_data(domino, job_ids, parallelize=False)
    t = datetime.datetime.now() - t
    logging.info(f"Queries succeeded in {str(round(t.total_seconds(),1))} seconds.")


### clean up data, merge with additional sources 
logging.info(f"Cleaning data...")
jobs = clean_jobs(jobs_raw, columns_to_expand, column_order, columns_to_datetime, goals, project_name)


### write list of jobs to csv
filename = f"{output_location}/{project_name}_audit_report_{datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d_%X%Z')}.csv"
logging.info(f"Saving report to: {filename}")
generate_report(jobs, filename)

### timing info
t = datetime.datetime.now() - t0
logging.info(f"Audit report generated in {str(round(t.total_seconds(),1))} seconds.")
    