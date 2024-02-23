from requests import post
from os import getenv
from json import dumps
from logs.manager import logger 
from datetime import datetime
from collections import Counter

# Get the environment variables
collector_id = getenv('LUMU_COLLECTOR_ID')
lumu_client_key = getenv('LUMU_CLIENT_KEY')
# Define the URL target
URL_TARGET = f"https://api.lumu.io/collectors/{collector_id}/dns/queries?key={lumu_client_key}"

def read_logs() -> list[dict]:
    """Read the logs from the lumu.log file and return the data in a list of dictionaries
        Returns:
            list[dict]: The logs data in a list of dictionaries"""
    inputs = []
    with open('./logs/lumu.log', 'r') as file:
        
        for line in file:
            # Divide each line by the separator ' - ' and extract the relevant parts
            sections = line.strip().split(' - ')
            date = sections[0] 
            level = sections[1]  
            message = sections[2] 
            # Append the extracted data to the inputs list for the logs view
            inputs.append({'date': date, 'level': level, 'message': message})
    return inputs

def send_to_api(payload: dict) -> bool:
    """ Send the payload to the Lumu API and return True if the action was successful
        Args:
            payload (dict): The payload to send to the Lumu API
        Returns:
            bool: True if the action was successful, False otherwise"""
    # Define the headers and send the payload to the Lumu API
    headers = {'Content-Type': 'application/json'}
    try:
        # Send the payload to the Lumu API
        response = post(URL_TARGET, headers=headers, data=dumps(payload))
        if response.status_code == 200:
            logger.info("Data send to Lumu API successfully")
        else:
            logger.error(f"Status code: {response.status_code}, Response: {response.text}")
        return True
    except Exception as e:
        logger.error(f"Exception: {e}")
        return False
 

def parse_log_file(chunk_raw,storage:list) -> list[dict]:
    """ Process the log file with a hunk size of 500
        Args:
            chunk_raw (list): The chunk of raw data to process
            storage (list): The storage list to store the host and client IP for the stats
        Returns:
            tuple: A tuple with the processed data and the storage list with the host and client IP for the stats"""
    chunk_cooked = []
                
    for line_bytes in chunk_raw:
        # Convert the line to a string and split it by spaces
        line_string = line_bytes.decode('utf-8')
        data = line_string.split(" ")
        # format the date to the API format
        date_base = data[0] + "T" + data[1]
        dt = datetime.strptime(date_base, "%d-%b-%YT%H:%M:%S.%f")
        date_format = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        # Extract the IP without the port
        ip_without_port = data[6].split("#")[0]
        # Append the processed data to the chunk_cooked list 
        chunk_cooked.append({
            "timestamp": date_format,
            "name": data[9],
            "client_ip": ip_without_port,
            "client_name": None,
            "type": data[11]
        })
        # Append the host and client IP to the storage list
        storage.append({
            "host": data[9],
            "client_ip": ip_without_port,
        })
    return chunk_cooked, storage

def get_stats(storage):
    """ Get the stats from the storage list
        Args:
            storage (list): The storage list with the host and client IP for the stats
        Returns:
            tuple: A tuple with the total records, the client IPs rank and the host rank in a dictionary format"""
    # get the total records
    total_records = len(storage)
    # Get the hosts and client IPs
    hosts = [item['host'] for item in storage]
    client_ips = [item['client_ip'] for item in storage]
    # Count the hosts and client IPs
    host_counts = Counter(hosts)
    client_ip_counts = Counter(client_ips)
    # Get the top 5 hosts and client IPs
    top_5_hosts = host_counts.most_common(5)
    top_5_client_ips = client_ip_counts.most_common(5)
    # Get the percentage of the top 5 hosts and client IPs
    top_5_hosts_percent = [(host, count, f"{(count / total_records) * 100:.2f}%") for host, count in top_5_hosts]
    top_5_client_ips_percent = [(ip, count, f"{(count / total_records) * 100:.2f}%") for ip, count in top_5_client_ips]

    return total_records, top_5_client_ips_percent,top_5_hosts_percent
            
def send_to_lumu(file_stream):
    """ Process the log file with a chunk size of 500 and send it to the Lumu API
    
        Args:
            file_stream (file): The file to process
        Returns:
            tuple: A tuple with the total records, the client IPs rank and the host rank in a dictionary format"""
            
    # Define the chunk size
    storage = []
    chunk_size = 500
    # Read the file lines
    lines = file_stream.readlines()
    total_lines = len(lines)
    logger.info("Total lines to process: %s", total_lines)
    # Process the file in chunks
    for i in range(0, total_lines, chunk_size):
        # Get the chunk of lines to process 
        chunk = lines[i:i+chunk_size]
        chunk_payload, storage = parse_log_file(chunk, storage)
        send_to_api(chunk_payload)
    total_records, client_ips_rank, host_rank = get_stats(storage)
    logger.info(f"Processed is gone successfully. Total records: {total_records}. Top 5 client IPs: {client_ips_rank}. Top 5 hosts: {host_rank}")
    return total_records, client_ips_rank, host_rank