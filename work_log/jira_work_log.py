import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import logging
import pandas as pd

# Set up logging
logging.basicConfig(filename='jira_work_log.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up your Jira credentials and project details
JIRA_URL = "https://your_tenant.atlassian.net"
PROJECT_KEYS = ["PS", "ADP"]  # List of project keys
USERNAME = "username"
API_TOKEN = "API_key"
SELECTED_MONTHS = [1]  # List of months (1-12)
SELECTED_YEARS = [2025]  # List of years

# Function to list all projects
def list_projects():
    url = f"{JIRA_URL}/rest/api/3/project"
    logging.debug(f"Requesting projects from URL: {url}")
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
    logging.debug(f"Response Status Code: {response.status_code}")
    logging.debug(f"Response Headers: {response.headers}")
    logging.debug(f"Response Text: {response.text}")
    response.raise_for_status()
    projects = response.json()
    for project in projects:
        logging.info(f"Project Key: {project['key']}, Project Name: {project['name']}")

# Function to get all issues in a project with pagination
def get_issues(project_key):
    url = f"{JIRA_URL}/rest/api/3/search"
    start_at = 0
    max_results = 50
    issues = []

    while True:
        query = {
            'jql': f'project={project_key}',
            'fields': 'key,summary,description,parent',
            'startAt': start_at,
            'maxResults': max_results
        }
        response = requests.get(url, params=query, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        logging.debug(f"Request URL: {response.url}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Text: {response.text}")
        response.raise_for_status()
        data = response.json()
        issues.extend(data.get('issues', []))
        if len(data.get('issues', [])) < max_results:
            break
        start_at += max_results

    return [{'key': issue['key'], 'summary': issue['fields']['summary'], 'description': issue['fields']['description'], 'parent': issue['fields'].get('parent', {}).get('key')} for issue in issues]

# Function to get issue details
def get_issue_details(issue_key):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
    response.raise_for_status()
    issue = response.json()
    logging.debug(f"Fetched parent issue details: {issue}")
    return {
        'key': issue['key'],
        'summary': issue['fields']['summary']
    }

# Function to get work logs for an issue
def get_worklogs(issue_key):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/worklog"
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
    logging.debug(f"Request URL: {response.url}")
    logging.debug(f"Response Status Code: {response.status_code}")
    logging.debug(f"Response Text: {response.text}")
    response.raise_for_status()
    return response.json().get('worklogs', [])

# Function to collect work logs by user for multiple projects, months, and years
def collect_worklogs_by_user(project_keys, selected_months, selected_years):
    worklogs_by_user = {}

    for project_key in project_keys:
        issues = get_issues(project_key)
        for issue in issues:
            issue_key = issue['key']
            issue_summary = issue['summary']
            issue_description = issue['description']
            parent_key = issue['parent']
            parent_summary = None
            if parent_key:
                parent_details = get_issue_details(parent_key)
                parent_summary = parent_details['summary']
                logging.debug(f"Parent Key: {parent_key}, Parent Summary: {parent_summary}")
            worklogs = get_worklogs(issue_key)
            for worklog in worklogs:
                started = worklog['started']
                worklog_date = datetime.strptime(started, '%Y-%m-%dT%H:%M:%S.%f%z')
                if worklog_date.month in selected_months and worklog_date.year in selected_years:
                    author = worklog['author']['displayName']
                    if author not in worklogs_by_user:
                        worklogs_by_user[author] = []
                    worklogs_by_user[author].append({
                        'issue': issue_key,
                        'summary': issue_summary,
                        'description': issue_description,
                        'parent': parent_key,
                        'parent_summary': parent_summary,
                        'timeSpent': worklog['timeSpent'],
                        'started': started,
                        'date': worklog_date.date().isoformat(),  # Convert date to string
                        'day_of_week': worklog_date.strftime('%A'),  # Day of the week
                        'month': worklog_date.month,  # Month
                        'year': worklog_date.year  # Year
                    })

    return worklogs_by_user

# Function to summarize work logs using pandas
def summarize_worklogs(worklogs_by_user):
    # Convert work logs to a DataFrame
    data = []
    for user, logs in worklogs_by_user.items():
        for log in logs:
            data.append({
                'user': user,
                'issue': log['issue'],
                'summary': log['summary'],
                'description': log['description'],
                'parent': log['parent'],
                'parent_summary': log['parent_summary'],
                'timeSpent': log['timeSpent'],
                'started': log['started'],
                'date': log['date'],
                'day_of_week': log['day_of_week'],
                'month': log['month'],
                'year': log['year']
            })
    df = pd.DataFrame(data)
    
    # Convert timeSpent to a numeric value (assuming format like '1d 1h 30m')
    def convert_time_spent(time_spent):
        days = 0
        hours = 0
        minutes = 0
        if 'd' in time_spent:
            days = int(time_spent.split('d')[0].strip())
            time_spent = time_spent.split('d')[1].strip()
        if 'h' in time_spent:
            hours = int(time_spent.split('h')[0].strip())
            time_spent = time_spent.split('h')[1].strip()
        if 'm' in time_spent:
            minutes = int(time_spent.split('m')[0].strip())
        return days * 24 * 60 + hours * 60 + minutes
    
    df['timeSpentMinutes'] = df['timeSpent'].apply(convert_time_spent)
    df['timeSpentHours'] = df['timeSpentMinutes'] / 60
    
    # Summarize work logs by user and date
    summary = df.groupby(['user', 'date', 'day_of_week', 'issue', 'summary', 'parent', 'parent_summary'])['timeSpentHours'].sum().reset_index()
    summary = summary.sort_values(by=['user', 'date', 'timeSpentHours'], ascending=[True, True, False])
    
    # Summarize total hours by user
    total_hours_by_user = df.groupby('user')['timeSpentHours'].sum().reset_index()
    total_hours_by_user = total_hours_by_user.rename(columns={'timeSpentHours': 'totalHours'})
    
    # Summarize total hours by parent ticket
    total_hours_by_parent = df.groupby(['parent', 'parent_summary'])['timeSpentHours'].sum().reset_index()
    total_hours_by_parent = total_hours_by_parent.rename(columns={'timeSpentHours': 'totalHours'})
    
    # Summarize total hours by month
    total_hours_by_month = df.groupby(['year', 'month'])['timeSpentHours'].sum().reset_index()
    total_hours_by_month = total_hours_by_month.rename(columns={'timeSpentHours': 'totalHours'})
    
    return summary, total_hours_by_user, total_hours_by_parent, total_hours_by_month

# Main function to execute the script
if __name__ == "__main__":
    # List all projects to verify the correct project key
    list_projects()
    
    # Collect work logs for the selected months and years
    worklogs_by_user = collect_worklogs_by_user(PROJECT_KEYS, SELECTED_MONTHS, SELECTED_YEARS)
    
    # Print work logs to console
    #print(json.dumps(worklogs_by_user, indent=4))
    
    # Save work logs to a JSON file
    with open('worklogs_by_user.json', 'w') as f:
        json.dump(worklogs_by_user, f, indent=4)
    
    # Log the work logs
    logging.info(json.dumps(worklogs_by_user, indent=4))
    
    # Summarize work logs using pandas
    summary, total_hours_by_user, total_hours_by_parent, total_hours_by_month = summarize_worklogs(worklogs_by_user)
    print(summary)
    print(total_hours_by_user)
    print(total_hours_by_parent)
    print(total_hours_by_month)
    
    # Save summary to a CSV file
    summary.to_csv('worklogs_summary.csv', index=False)
    
    # Save total hours by user to a CSV file
    total_hours_by_user.to_csv('total_hours_by_user.csv', index=False)
    
    # Save total hours by parent ticket to a CSV file
    total_hours_by_parent.to_csv('total_hours_by_parent.csv', index=False)
    
    # Save total hours by month to a CSV file
    total_hours_by_month.to_csv('total_hours_by_month.csv', index=False)
