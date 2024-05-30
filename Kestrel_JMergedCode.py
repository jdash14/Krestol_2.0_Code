import subprocess
import requests
import re
import json
from jproperties import Properties
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class SentenceSimilarity:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/paraphrase-xlm-r-multilingual-v1')

    def run(self, sentence1, sentence2, sentence3):
        embeddings1 = self.model.encode([sentence1, sentence2, sentence3])
        output = cosine_similarity(embeddings1, embeddings1)[0, 1]
        return output

class Dummy:
    AnalyticsURlCount = 2

    def __init__(self, reportid, type, result_text):
        self.reportid = reportid
        self.type = type
        self.name = None
        self.result_text = result_text
        print("BugtriageReport instance created with reportid:", self.reportid, "and type:", self.type)
        print(self)

    def __str__(self):
        try:
            yabCommand = (
                "yab -s tech-issue-tracker --caller yab-vkamju --grpc-max-response-size 90971520 --request '{"
                "\"type\":[\"%s\"],\"report_uuid\":\"%s\"}' --procedure "
                "'uber.mobile.apphealth.TechIssueTracker/GetBugReportDetail' --header 'studio-caller:skamma3' "
                "--header 'x-uber-source:studio' --header 'x-uber-uuid:faab28af-5cc6-43fc-9241-b5711059e243' "
                "--header 'jaeger-debug-id:api-explorer-vkamju' --header "
                "'uberctx-tenancy:uber/testing/api-explorer/95a2-4803-8a63-12ebf0dffb9f' --peer '127.0.0.1:5435' "
                "--timeout 900000ms" % (self.reportid, self.type)
            )

            reactivateResponse = subprocess.check_output(yabCommand, shell=True)
            d = json.loads(reactivateResponse)
            result = ""
            unique_names = set()
            for item in d['body']['analytics_logs']:
                if "name" in item and ('error' in item['name'] or 'failure' in item['name']):
                    self.name = item['name']
                    if self.name not in unique_names:
                        result = "\n Type:" + (item['type']).upper() + " \n Name:" + self.name + "\n" + result
                        unique_names.add(self.name)
            SHEET_ID = '1cOb6SmZ8IOjJeHCFMU8RBFlwkjFmzPMuJgUE0J3A9rM'
            SHEET_NAME = 'Sheet11'
            global AnalyticsURlCount
            gc = gspread.service_account('UberCredentials.json')
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.worksheet(SHEET_NAME)
            if self.name != 'network_call_capturing_failure':
                print(result)
        except Exception as err:
            print("error report", err)
        return f"{self.reportid} {self.type}"

class BugtriageReport:
    NetworkURlCount = 2
    similarity_score_count = 0

    def __init__(self, reportid, type, result_text, url):
        self.reportid = reportid
        self.type = type
        self.url = url
        self.result_text = result_text
        self.uuid = readPropertyValue("TECHISSUETRACKER_API")
        self.api = readPropertyValue("TECHISSUETRACKER_API")
        self.port = readPropertyValue("PORT")
        self.network_logs = []
        self.analytics_logs = []
        print(self)

    def __str__(self):
        try:
            yabCommand = (
                "yab -s tech-issue-tracker --caller yab-vuppul1 --grpc-max-response-size 60971520 --request '{"
                "\"type\":[\"%s\"],\"report_uuid\":\"%s\"}' --procedure 'uber.mobile.apphealth.TechIssueTracker/GetBugReportDetail' "
                "--header 'studio-caller:vuppul1' --header 'x-uber-source:studio' --header 'x-uber-uuid:%s' "
                "--header 'jaeger-debug-id:api-explorer-vuppul1' --header 'uberctx-tenancy:uber/testing/api-explorer/95a2-4803-8a63-12ebf0dffb9f' "
                "--peer '%s:%s' --timeout 60000ms" % (self.reportid, self.type, self.uuid, self.api, self.port)
            )
            reactivateResponse = subprocess.check_output(yabCommand, shell=True)
            d = json.loads(reactivateResponse)
            i = 1
            unique_names = set()
            result = ""
            Consoleresult = ""
            unique_names_ConsoleLogs = set()
            if "network_logs" in d['body']:
                for item in d['body']['network_logs']:
                    if "status_code" in item and int(item['status_code']) >= 400:
                        network_log = {
                            "status_code": item['status_code'],
                            "endpoint_path": item['endpoint_path'],
                            "response_body": item['response_body']
                        }
                        if network_log not in self.network_logs:
                            self.network_logs.append(network_log)
            if "analytics_logs" in d['body']:
                for item in d['body']['analytics_logs']:
                    if "name" in item and ('error' in item['name'] or 'failure' in item['name']):
                        name = item['name']
                        if name not in unique_names:
                            result = "\n *Analytical Logs:* \n *Type* :" + (item['type']).upper() + " \n *Name* :" + name + "\n" + result
                            unique_names.add(name)
                        sent3 = name
                        sent1 = name
                        sent2 = name
                        analyzer = SentenceSimilarity()
                        similarity_score = analyzer.run(sent1, sent2, sent3)
                        if float(similarity_score) >= 0.55:
                            self.analytics_logs.append({
                                "type": item['type'].upper(),
                                "name": item['name']
                            })
                            similarity_score_count += 1
            if "console_logs" in d['body']:
                for item in d['body']['console_logs']:
                    if 'message' in item and ('warning' in item['level']):
                        message = item['message']
                        if message not in unique_names_ConsoleLogs and (("error" in item['message'] and "HTTPRequest" in item['message']) or ("has leaked" in item['message'])):
                            result = "\n Level:" + (item['level']).upper() + " \n Message:" + item['message'] + "\n" + Consoleresult
                            unique_names_ConsoleLogs.add(message)
            result += self.construct_table() # Move construct_table call here
            return result # Ensure to return a string even if empty
        except Exception as e:
            print("Error in BugtriageReport:", e)
            return "Error occurred in BugtriageReport __str__ method"

    def construct_table(self):
        table = "Bug Valid | Severity | Logs\n"
        table += "-" * 77 + "\n"

        for network_log in self.network_logs:
            table += f"Yes | Core Flow | Network Log\n"
            table += " " * 32 + f"| {network_log['status_code']} | {network_log['endpoint_path']} | \n"

        for analytics_log in self.analytics_logs:
            table += f"Yes | Core Flow | Analytics Log\n"
            table += " " * 32 + f"| {analytics_log['type']} | {analytics_log['name']} | \n"

        return table

def extract_url_from_text(text):
    if "https://wisdom" in text:
        url_pattern = r'\[([^]]+)\]'
        match = re.search(url_pattern, text)
        if match:
            return match.group(1)
    return None

class JiraUpdate:
    def __init__(self, url, result, bugtriage_reports):
        self.url = url
        self.result = result
        self.bugtriage_reports = bugtriage_reports
        token = readPropertyValue("TOKEN")
        headers = {
            "cache-control": "no-cache",
            "Authorization": "Bearer " + token
        }
        data = {
            "body": self.construct_comment()
        }
        if len(result.strip()):
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                print(f"Comment added successfully to Jira issue")
            else:
                print(f"Failed to add comment to Jira issue. Status code: {response.status_code}, Response: {response.json()}")

    def construct_comment(self):
        comment = self.result + "\n\n"
        for bugtriage_report in self.bugtriage_reports:
            comment += bugtriage_report.construct_table() + "\n\n"
        return comment

def readPropertyValue(key):
    configs = Properties()
    with open('config.properties', 'rb') as config_file:
        configs.load(config_file)
    value = str(configs.get(key).data)
    return value

try:
    token = readPropertyValue("TOKEN")
    filterid = readPropertyValue("FILTERID")
    url = f"https://t3.uberinternal.com/rest/api/2/search?jql=filter={filterid}"
    headers = {
        "cache-control": "no-cache",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    d = response.json()
    for item in d['issues']:
        jira_link = f"https://t3.uberinternal.com/rest/api/2/issue/{item['key']}/comment"
        url = extract_url_from_text(item['fields']['description'])
        print("URL is", url)
        if url:
            first_string = url.split('/')
            last_string = first_string[6]
            print("Last string extracted from URL:", last_string)
            result_text = "Sample result text" # Define your result text here
            network_bugrep = BugtriageReport("DETAIL_TYPE_NETWORK_LOG", str(last_string), result_text, url)
            analytics_bugrep = BugtriageReport("DETAIL_TYPE_ANALYTICS_LOG", str(last_string), result_text, url)
            # Creating a list of BugtriageReport instances
            bugtriage_reports = [network_bugrep, analytics_bugrep]
            # Creating a single JiraUpdate instance with both reports
            jira_update = JiraUpdate(jira_link, result_text, bugtriage_reports)
        else:
            print("URL not found in the string.")
except Exception as e:
    print("Error - ", e)