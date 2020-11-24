# Modules import
import requests
from requests.auth import HTTPBasicAuth
import time
import sys
import json

# Disable SSL warnings. Not needed in production environments with valid certificates
import urllib3
urllib3.disable_warnings()

# Authentication
BASE_URL = '' # Example BASE_URL = 'https://sandboxdnac.cisco.com'
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = '' # Example USERNAME = 'devnetuser'
PASSWORD = '' # Example PASSWORD = 'Cisco123!'

#修改登陆凭证
def change_Authentication(DNACip,Username,Password):
    global BASE_URL
    global USERNAME
    global PASSWORD
    BASE_URL = DNACip
    USERNAME = Username
    PASSWORD = Password
    response = requests.post(BASE_URL + '/dna/system/api/v1/auth/token',
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             verify=False,timeout=3).json()
    return response
# URLs
DEVICES_BY_SERIAL_URL = '/dna/intent/api/v1/network-device/serial-number/{serial_number}'
NETWORK_URL = '/dna/intent/api/v1/network/{site_id}'
SITE_DEVICE_URL = '/dna/intent/api/v1/site/{site_id}/device'
SITE_URL = '/dna/intent/api/v1/site'
TASK_BY_ID_URL = '/dna/intent/api/v1/task/{task_id}'
TEMPLATE_DEPLOY_URL = '/dna/intent/api/v1/template-programmer/template/deploy'
TEMPLATE_PROJECT_URL = '/dna/intent/api/v1/template-programmer/project'
TEMPLATE_URL = '/dna/intent/api/v1/template-programmer/project/{project_id}/template'
TEMPLATE_VERSION_URL = '/dna/intent/api/v1/template-programmer/template/version'
GET_TEMPLEATE_LIST='/dna/intent/api/v1/template-programmer/template'
# URLs
DEVICES_URL = '/dna/intent/api/v1/network-device'
PATH_TRACE_URL = '/dna/intent/api/v1/flow-analysis'
PATH_TRACE_ID_URL = '/dna/intent/api/v1/flow-analysis/{flow_analysis_id}'

# Get Authentication token
def get_dnac_jwt_token():
    response = requests.post(BASE_URL + AUTH_URL,
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             verify=False,timeout=3).json()
    token = response['Token']
    return token

# Get list of sites
def get_sites(headers):
    response = requests.get(BASE_URL + SITE_URL,
                            headers=headers, verify=False)
    return response.json()['response']



# Create path trace
def create_path_trace(headers, path_trace_payload):
    response = requests.post(BASE_URL + PATH_TRACE_URL, headers=headers, 
                             json=path_trace_payload, verify=False)
    return response.json()['response'] 
    
# Get path trace result
def get_path_trace_by_id(headers, flow_analysis_id):
    response = requests.get(BASE_URL + PATH_TRACE_ID_URL.format(flow_analysis_id=flow_analysis_id), 
                            headers=headers, verify=False)
    return response.json()['response']

    
#返回站点列表
def get_site_list():
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = get_sites(headers)
    site_list = []
    for site in response:
        site_list.append([site['name'],site['siteNameHierarchy'],site['id']])
    return site_list

#返回站点的名称列表
def get_site_name_list():
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = get_sites(headers)
    site_name_list = []
    for site in response:
        site_name_list.append(site['name'])
    #print(site_name_list)
    return site_name_list

# Get list of devices
def get_devices(headers, query_string_params):
    response = requests.get(BASE_URL + DEVICES_URL,
                            headers = headers,
                            params = query_string_params,
                            verify=False)
    return response.json()['response']
    
def get_path_list(start,end):
    # obtain the Cisco DNA Center Auth Token
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}

    # Get src device IP
    print('Printing source device IP ...')
    query_string_params = {'hostname': start}
    response = get_devices(headers, query_string_params)
    src_ip_address = response[0]['managementIpAddress']
    print(src_ip_address)

    # print devices list
    print('\nPrinting destination device IP ...')
    query_string_params = {'hostname': end}
    response = get_devices(headers, query_string_params)
    dst_ip_address = response[0]['managementIpAddress']
    print(dst_ip_address)

    # Generate a new path trace
    print('\nPrinting flow analysis id ...')
    path_trace_payload = {
        'sourceIP': src_ip_address,
        'destIP': dst_ip_address,
        'inclusions': [
            'INTERFACE-STATS',
            'DEVICE-STATS',
            'ACL-TRACE',
            'QOS-STATS'
        ],
        'protocol': 'icmp'
    }
    response = create_path_trace(headers, path_trace_payload)
    flow_analysis_id = response['flowAnalysisId']
    print(flow_analysis_id)

    # Waiting until the path trace is done
    time.sleep(10)

    # Get path trace result
    print('\nPrinting path trace result ...')
    response = get_path_trace_by_id(headers, flow_analysis_id)
    path_list = []
    path_interface_list = []
    print(json.dumps(response,sort_keys=True,indent=4))
    for item in response['networkElementsInfo']:
        path_list.append([item["id"],item["ip"],item["name"],item["role"]])
    for item in response['networkElementsInfo']:
        #print(json.dumps(item,sort_keys=True,indent=4))
        if 'egressInterface'in item:
            path_interface_list.append([item["egressInterface"]["physicalInterface"]["name"],item["egressInterface"]["physicalInterface"]["interfaceStatsCollection"]])
        if 'ingressInterface'in item:
            path_interface_list.append([item["ingressInterface"]["physicalInterface"]["name"],item["ingressInterface"]["physicalInterface"]["interfaceStatsCollection"]])
        #path_interface_list.append([item["egressInterface"]["physicalInterface"]["name"],item["egressInterface"]["physicalInterface"]["interfaceStatsCollection"]
        #,item["ingressInterface"]["virtualInterface"]["name"],item["ingressInterface"]["virtualInterface"]["interfaceStatsCollection"]])
    #print(json.dumps(response,sort_keys=True,indent=4))
    #print(path_interface_list)
    return path_list,path_interface_list
    
def get_device_serialNumber():
    token = get_dnac_jwt_token()
    url = "{}/api/v1/network-device".format(BASE_URL)
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    #print(json.dumps(data,sort_keys=True,indent=4))
    device_serialNumber_list = []
    for item in data['response']:
    #    print(json.dumps(item,sort_keys=True,indent=4))
    #    if(item['serialNumber'] != null):
        device_serialNumber_list.append([item["hostname"],item['serialNumber']])
    #print(device_serialNumber_list)
    return device_serialNumber_list

if __name__ == "__main__":
    response=change_Authentication('https://10.14.40.220','admin','Dnac123!')
    #response=change_Authentication('https://sandboxdnac2.cisco.com','devnetuser','Cisco123!')
    print(response)
    #response = get_site_list()
    #print(response)
    (path_list,path_interface_list)=get_path_list('Pod3-Fusion.abc.com','Pod3-Edge.abc.com')
    print(path_list)
    print(path_interface_list)
    #response =  get_device_serialNumber()
    #response =  get_site_name_list()
    #response =get_template_name_list()
    #print(response)
    #get_template_name_list()
    #response = device_provisioning("Testplan","FOC2402X0TU","172.30.200.5","4399.com","172.30.200.1","172.30.200.5","IPsec 2")
    #print(json.dumps(response,sort_keys=True,indent=4))
    #response = device_provisioning("Testplan","FOC2402X0TU","172.30.200.5","4399.com","172.30.200.1","172.30.200.5","IPsec 2 Branch for Cloud Router - System Default")
    #print(json.dumps(response,sort_keys=True,indent=4))
    #response = device_provisioning("Testplan","FCW2402D060","172.30.200.5","4399.com","172.30.200.1","172.30.200.5","IPsec 2 Branch for Cloud Router - System Default")
    #print(json.dumps(response,sort_keys=True,indent=4))