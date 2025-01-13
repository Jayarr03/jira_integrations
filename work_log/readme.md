# Jira Work Log Summary

This script collects work logs from Jira for specified projects, months, and years, and summarizes the data using pandas. The summaries include total hours worked by user, by parent ticket, and by month.

## Prerequisites

- Python 3.x
- Pandas library

## Installation

1. Clone the repository or download the script.
2. Install the required Python packages:

    ```sh
    pip install pandas requests
    ```

## Configuration

Update the following variables in the script with your Jira credentials and project details:

- `JIRA_URL`: The base URL of your Jira instance.
- `PROJECT_KEYS`: A list of project keys to collect work logs from.
- `USERNAME`: Your Jira username.
- `API_TOKEN`: Your Jira API token.
- `SELECTED_MONTHS`: A list of months (1-12) to collect work logs for.
- `SELECTED_YEARS`: A list of years to collect work logs for.

Example configuration:

```python
JIRA_URL = "https://your-jira-instance.atlassian.net"
PROJECT_KEYS = ["PROJECT1", "PROJECT2"]
USERNAME = "your-email@example.com"
API_TOKEN = "your-api-token"
SELECTED_MONTHS = [1, 2, 3]  # January, February, March
SELECTED_YEARS = [2023, 2024]

Sure, here's a `README.md` file for your 

jira_work_log.py

 script.

### README.md

```markdown
# Jira Work Log Summary

This script collects work logs from Jira for specified projects, months, and years, and summarizes the data using pandas. The summaries include total hours worked by user, by parent ticket, and by month.

## Prerequisites

- Python 3.x
- Pandas library

## Installation

1. Clone the repository or download the script.
2. Install the required Python packages:

    ```sh
    pip install pandas requests
    ```

## Configuration

Update the following variables in the script with your Jira credentials and project details:

- `JIRA_URL`: The base URL of your Jira instance.
- `PROJECT_KEYS`: A list of project keys to collect work logs from.
- `USERNAME`: Your Jira username.
- `API_TOKEN`: Your Jira API token.
- `SELECTED_MONTHS`: A list of months (1-12) to collect work logs for.
- `SELECTED_YEARS`: A list of years to collect work logs for.

Example configuration:

```python
JIRA_URL = "https://your-jira-instance.atlassian.net"
PROJECT_KEYS = ["PROJECT1", "PROJECT2"]
USERNAME = "your-email@example.com"
API_TOKEN = "your-api-token"
SELECTED_MONTHS = [1, 2, 3]  # January, February, March
SELECTED_YEARS = [2023, 2024]
```

## Usage

Run the script:

```sh
python jira_work_log.py
```

The script will:

1. List all projects to verify the correct project keys.
2. Collect work logs for the specified projects, months, and years.
3. Print the collected work logs to the console.
4. Save the collected work logs to a JSON file (

worklogs_by_user.json

).
5. Log the collected work logs.
6. Summarize the work logs using pandas.
7. Print the summaries to the console.
8. Save the summaries to CSV files:
    - `worklogs_summary.csv`: Detailed summary of work logs.
    - 

total_hours_by_user.csv

: Total hours worked by user.
    - 

total_hours_by_parent.csv

: Total hours worked by parent ticket.
    - 

total_hours_by_month.csv

: Total hours worked by month.

## Output

The script generates the following output files:

worklogs_by_user.json

: JSON file containing the collected work logs.
- `worklogs_summary.csv`: CSV file containing the detailed summary of work logs.
- 

total_hours_by_user.csv

: CSV file containing the total hours worked by user.
- 

total_hours_by_parent.csv

: CSV file containing the total hours worked by parent ticket.
- 

total_hours_by_month.csv

: CSV file containing the total hours worked by month.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
```
