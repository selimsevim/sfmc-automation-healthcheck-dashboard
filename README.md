# SFMC Automation Healthcheck Dashboard
## Overview

The SFMC Automation Healthcheck Dashboard is a Streamlit-based monitoring tool designed to help Salesforce Marketing Cloud (SFMC) users track, analyze, and optimize their automations and activities. It provides real-time insights into automation execution, performance trends, and potential risks.

## Key Features

- **Automation Performance Tracking**: Monitors execution times, statuses, and error details of automations.
- **Historical Trend Analysis**: Compares automation performance across different timeframes to identify anomalies.
- **Risk Identification**: Detects long-running automations, delays, and potential timeout risks.
- **Overlapping Automations**: Identifies automations running simultaneously, which may cause execution conflicts.
- **Rush Hour Detection**: Highlights peak execution times to help optimize scheduling.
- **Activity-Level Insights**: Analyzes individual queries and scripts that may exceed execution limits.
- **Business Unit Filtering**: Allows users to filter automation data based on Business Unit (mID).
- **Interactive Data Visualization**: Uses **Plotly** and **Streamlit** to provide real-time insights with charts and tables.
- **Custom Timeframe Selection**: Enables users to set specific date ranges for detailed analysis.

![Screenshot](/screenshots/1.png)

![Screenshot](/screenshots/2.png)

![Screenshot](/screenshots/3.png)

![Screenshot](/screenshots/4.png)

![Screenshot](/screenshots/5.png)

![Screenshot](/screenshots/6.png)

![Screenshot](/screenshots/7.png)

![Screenshot](/screenshots/8.png)

![Screenshot](/screenshots/9.png)

## Installation
### Clone the Repository:

```
git clone https://github.com/yourusername/sfmc-automation-healthcheck-dashboard.git
cd sfmc-automation-healthcheck-dashboard
```
### Create a Virtual Environment:
```
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
```
### Install Dependencies:
```
pip install -r requirements.txt
```
### Prepare Data Files

Ensure you export CSV files from two data extensions having the right fields below and put them in the working directory:

- **Data Files:**
  - **`automation_data.csv`** – Contains automation execution details.
  - **`automation_activity_data.csv`** – Contains activity-level execution logs.

### Run the Dashboard:
```
streamlit run app.py
```

## Data Structure 

Automation Instances:
| Column                                   | Type    | Length | Nullable | Primary Key |
|------------------------------------------|---------|--------|----------|-------------|
| `AutomationInstanceID`                   | Text  | 255     | ❌       | ✔          |
| `AutomationName`                         | Text  | 255    | ❌       | ❌           |
| `AutomationCustomerKey`                  | Text  | 255    | ❌       | ❌           |
| `AutomationInstanceScheduledTime_UTC`    | Date | N/A    | ✔       | ❌          |
| `AutomationInstanceStartTime_UTC`        | Date | N/A    | ✔       | ❌          |
| `AutomationInstanceEndTime_UTC`          | Date | N/A    | ✔       | ❌          |
| `AutomationInstanceStatus`               | Text  | 50     | ❌       | ❌          |
| `AutomationInstanceActivityErrorDetails` | Text  | 4000   | ✔       | ❌          |
| `MemberID`                               | Text  | 50     | ❌       | ❌          |

Automation Activity Instances:
| Column                                   | Type    | Length | Nullable | Primary Key |
|------------------------------------------|---------|--------|----------|-------------|
| `AutomationInstanceID`                   | Text  | 50     | ❌       | ✔          |
| `AutomationName`                         | Text  | 255    | ❌       | ❌           |
| `AutomationCustomerKey`                  | Text  | 255    | ❌       | ❌           |
| `ActivityType`                           | Text  | 255    | ❌       | ❌           |
| `ActivityName`                           | Text  | 255    | ❌       | ❌           |
| `ActivityInstanceID`                     | Text  | 255    | ❌       | ❌           |
| `AutomationInstanceStartTime_UTC`        | Date | N/A    | ✔       | ❌          |
| `AutomationInstanceEndTime_UTC`          | Date | N/A    | ✔       | ❌          |


## Example SQLs:

Retrieving Automation Instances:

```
SELECT 
    AutomationInstanceID, 
    AutomationName, 
    AutomationCustomerKey, 
    AutomationInstanceScheduledTime_UTC, 
    AutomationInstanceStartTime_UTC, 
    AutomationInstanceEndTime_UTC, 
    AutomationInstanceStatus, 
    AutomationInstanceActivityErrorDetails, 
    MemberID
FROM [_automationinstance]
WHERE AutomationInstanceIsRunOnce = 0

```
Retrieving Automation Activity Instances:
```
SELECT 
    AutomationInstanceID, 
    AutomationName, 
    AutomationCustomerKey, 
    ActivityType, 
    ActivityName, 
    ActivityInstanceID, 
    AutomationInstanceStartTime_UTC, 
    AutomationInstanceEndTime_UTC
FROM [_automationactivityinstance]
```

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request if you find a bug or have an idea for improvement.

## License

This project is licensed under the MIT License.
