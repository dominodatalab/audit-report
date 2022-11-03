### functions.py

from packages import *
from classes import *

def get_jobs(domino, project_id):
    """
    This will return a list of all job IDs from the selected project.
    TODO: Use the pagination instead of setting hard limit of 1000
    TODO: allow list of project IDs 
    """
    endpoint = f"/v4/jobs?projectId={project_id}&page_size=1000" 
    url = f"{domino.api_host}{endpoint}"
    headers = {
      'X-Domino-api-key': domino.api_key
    }
    
    r = requests.request("GET", url, headers=headers)
    r = json.loads(r.text)['jobs']
    
    job_ids = []
    for job in r:
        job_ids.append(job['id'])
    return job_ids


def aggregate_job_data(domino, job_ids, parallelize=True):
    jobs = {}
    if parallelize:
        def process(job_id):
            return get_job_data(domino, job_id)
        result = Parallel(n_jobs=os.cpu_count())(delayed(process)(job_id) for job_id in job_ids)
        for job in result:
            jobs[job['id']] = job
    else:
        for job_id in job_ids:
            job = get_job_data(domino, job_id)
            jobs[job['id']] = job
    return jobs


def get_job_data(domino, job_id):
    endpoints = [f"/v4/jobs/{job_id}",
                 f"/v4/jobs/{job_id}/runtimeExecutionDetails",
                 f"/v4/jobs/{job_id}/comments",
                 f"/v4/jobs/job/{job_id}/artifactsInfo"]
    headers = {
      'X-Domino-api-key': domino.api_key
    }
    result = {}
    for endpoint in endpoints:
        url = f"{domino.api_host}{endpoint}"
        r = requests.request("GET", url, headers=headers)
        r = json.loads(r.text)
        if r is not None:
            result.update(r)
    return result


def get_goals(domino, project_id):
    headers = {
      'X-Domino-api-key': domino.api_key
    }
    url = f"{domino.api_host}/v4/projectManagement/{project_id}/goals"
    r = requests.request("GET", url, headers=headers)
    r = json.loads(r.text)
    goals = {}
    for goal in r:
        goals[goal['id']] = goal['title']
    return goals
    

def generate_report(data, filename):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_csv(filename, header=True, index=False)

    
def expand(c, job, jobs):
    for x in jobs[job][c]:
        jobs[job][f'{c}-{x}'] = jobs[job][c].get(x)
    jobs[job].pop(c)
    
    
def convert_datetime(time_str):
    return datetime.datetime.fromtimestamp(time_str / 1e3, tz=datetime.timezone.utc).strftime('%F %X:%f %Z')


def clean_comments(job):
    comments = []
    for c in job['comments']:
        comment = {
            'comment-username': c['commenter']['username'],
            'comment-timestamp': convert_datetime(c['created']),
            'comment-value': c['commentBody']['value']
        }
        comments.append(comment)
    return comments


def clean_goals(job, jobs, goals):
    goal_names = []
    if len(jobs[job]['goalIds']) > 0:
        for goal_id in jobs[job]['goalIds']:
            goal_names.append(goals[goal_id])
    return goal_names


def sorter(job, jobs, column_order):
    result = {}
    for c in column_order:
        result[c] = jobs[job].get(c)
    return result


def clean_jobs(jobs, columns_to_expand, column_order, columns_to_datetime, goals, project_name):
    for job in jobs:
        for c in (c for c in list(jobs[job]) if c in columns_to_expand):
            expand(c, job, jobs)
        for c in (c for c in jobs[job] if c in columns_to_datetime):
            jobs[job][c] = convert_datetime(jobs[job][c])
        if 'comments' in jobs[job].keys():
            jobs[job]['comments'] = clean_comments(jobs[job])
        jobs[job]['goals'] = clean_goals(job, jobs, goals)
        jobs[job].pop('goalIds')
        jobs[job]['projectName'] = project_name
        jobs[job] = sorter(job, jobs, column_order)
    return jobs
    

