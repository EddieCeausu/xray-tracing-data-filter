import boto3
import json
import time
from datetime import datetime

# Initialize AWS X-Ray client
xray_client = boto3.client("xray")
# Get the current time in Epoch
epoch_time = int(round(time.time()))
current_time = datetime.fromtimestamp(epoch_time)
# Get the time 6 hours ago in Epoch. Modify the 6 to get times 1-24 hours in the past
time_6_hours_ago = datetime.fromtimestamp(epoch_time - (6 * 3600))
filter_name = ""

filter_expression = "service(id(name: \"%s\", type: \"AWS::lambda::Function\")) { error }" % filter_name

def get_trace_summaries(start_time, end_time, filter_expression):
    response = xray_client.get_trace_summaries(
        StartTime=str(start_time),
        EndTime=str(end_time),
        FilterExpression=filter_expression
    )
    # Get the trace IDs from the response
    trace_ids = [summary['Id'] for summary in response.get('TraceSummaries', [])]
    return trace_ids

# This was implemented for testing purposes.
def open_traces():
    with open('data.txt', 'r') as file:
            data=file.read().replace('\n', ' ')
    data = data.split()
    print(data)
    return data


# Filter the segments for Activity #3 and if it has an error => Then add it to the filtered_subsegments list 
def filter_subsegments(trace_segments):
    filtered_subsegments = []
    for trace in trace_segments["Traces"]:
        for segment in trace["Segments"]:
            for subsegment in segment["Document"]["subsegments"]:
                if subsegment["name"] == "Attempt #3" and subsegment.get("error", False): # Update here to allow for customized Filtering
                    filtered_subsegments.append(subsegment)

    # Print the filtered subsegments
    for subsegment in filtered_subsegments:
        print(json.dumps(subsegment, indent=4))



def main():
     # For testing we will open the traces from a file and recursively make api calls on them
     #trace_ids = open_traces()
     # Get the trace segments
     current_traces = get_trace_summaries(time_6_hours_ago, current_time, filter_expression)
     # Filter the segments
     for trace in current_traces:
        try:
            trace_segments = xray_client.batch_get_traces(
                TraceIds=[trace]
                )
            filter_subsegments(trace_segments)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
