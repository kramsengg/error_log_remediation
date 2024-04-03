from diagrams import Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.saas.logging import Datadog
from diagrams.programming.framework import Flask
from diagrams.custom import Custom
graph_attr = {
    "fontsize": "45",
}

with Diagram("Error Log Remediation - Automation", show=False, graph_attr=graph_attr):
    cc_jira = Custom("Jira/Confluence", "./src/images/jira.png")
    cc_openai = Custom("OpenAI", "./src/images/OpenAI_Green.png")
    EC2("EC2-WebApps") >> Edge(label="Pushing logs") >> \
    Datadog("Centralized Log System") >> Edge(label="Monitoring alert") >> \
    Datadog("Monitoring Log Alert") >> Edge(label="Notification to webhook") >> \
    Flask("Python Flask App - Webhook") >> Edge(label="Process and get remediation using OpenAI") >> \
    cc_openai >> Edge(label="Create doc/JIRS ticket with remediation") >> \
    cc_jira