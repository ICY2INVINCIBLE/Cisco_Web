import requests
import json
from requests.auth import HTTPBasicAuth
BASE_URL = 'https://10.14.40.220' # Example BASE_URL = 'https://sandboxdnac.cisco.com'
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = 'admin' # Example USERNAME = 'devnetuser'
PASSWORD = 'Dnac123!' # Example PASSWORD = 'Cisco123!'

SITE_URL = '/dna/intent/api/v1/site'
def get_token(dnac_ip,dnac_user,dnac_pwd):#dnac_ip = 接入地址  dnac_user=账户  dnac_pwd=密码
    requests.packages.urllib3.disable_warnings()
    token = requests.post(
       '{}/dna/system/api/v1/auth/token'.format(dnac_ip),
       auth=HTTPBasicAuth(
           username= dnac_user,
           password= dnac_pwd
       ),
      verify=False,
      timeout=3
    )
    data = token.json()
    return data#返回的token需要储存


def get_dnac_jwt_token():
    #print(BASE_URL + AUTH_URL)
    response = requests.post(BASE_URL + AUTH_URL,
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             verify=False, timeout=3).json()
    print(response)
    token = response['Token']
    return token

# Get list of sites
def get_sites1(headers):
    response = requests.get(BASE_URL + SITE_URL,
                            headers=headers, verify=False)
    return response.json()['response']

  
# 返回站点的名称列表
def get_site_name_list1():
    token = get_dnac_jwt_token1()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = get_sites1(headers)
    site_name_list = []
    for site in response:
        site_name_list.append(site['siteNameHierarchy'])
    return site_name_list  
    
    
def get_sites(headers):
    response = requests.get(BASE_URL + SITE_URL,
                            headers=headers, verify=False)
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

import test

if __name__ == '__main__':
    #token=get_dnac_jwt_token1()
    #list = get_device_health(token,BASE_URL)
    path_list, path_interface_list = get_path_list('Pod2-Fusion.abc.com','Pod2-Edge.abc.com')
    print(path_list)
    print(path_interface_list)
    #print(json.dumps(response,sort_keys=True,indent=4))
    #print(get_site_name_list1())
    #test.app.run(port=5080)
    
    #print(get_site_name_list1())
    #print(get_token('https://10.14.40.220','admin','Dnac123!'))
    #token = get_token('https://10.14.40.220','admin','Dnac123!')
    #print(get_device(token['Token'],'https://10.14.40.220'))