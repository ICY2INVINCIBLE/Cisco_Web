import requests
import json
from requests.auth import HTTPBasicAuth
requests.adapters.DEFAULT_RETRIES = 10
s = requests.session()
s.keep_alive = False

def get_token(dnac_ip,dnac_user,dnac_pwd):#dnac_ip = 接入地址  dnac_user=账户  dnac_pwd=密码
    requests.packages.urllib3.disable_warnings()
    token = requests.post(
       '{}/dna/system/api/v1/auth/token'.format(dnac_ip),
       auth=HTTPBasicAuth(
           username= dnac_user,
           password= dnac_pwd
       ),
      headers={'content-type': 'application/json'},
      verify=False,
    )
    data = token.json()
    return data#返回的token需要储存


def get_device(token,dnac_ip):

    url = "{}/api/v1/network-device".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    data = response.json()
    #print(data)
    list = [['Hostname','Platform Id','MacAddress','Software Type','Software Version','Up Time' ]]
    for item in data['response']:
        if(item["hostname"] == None):
            continue
        list.append([item["hostname"],item["platformId"],item["macAddress"],item["softwareType"],item["softwareVersion"],item["upTime"]])
    return list
    
def get_device_type(token,dnac_ip):

    #requests.packages.urllib3.disable_warnings()
    url = "{}/api/v1/network-device".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    data = response.json()
    list_device = []
    list_device_num = []
    for item in data['response']:
        if(item["platformId"] in list_device):
            list_device_num[list_device.index(item["platformId"])] = list_device_num[list_device.index(item["platformId"])] + 1
        if(not(item["platformId"] in list_device)):
            list_device.append(item["platformId"])
            list_device_num.append(1)
    list = [list_device,list_device_num]
    return list
    
def get_device_software(token,dnac_ip):

    #requests.packages.urllib3.disable_warnings()
    url = "{}/api/v1/network-device".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    data = response.json()
    list_device = []
    list_device_num = []
    for item in data['response']:
        if(item["softwareType"] in list_device):
            list_device_num[list_device.index(item["softwareType"])] = list_device_num[list_device.index(item["softwareType"])] + 1
        if(not(item["softwareType"] in list_device)):
            list_device.append(item["softwareType"])
            list_device_num.append(1)
    list = [list_device,list_device_num]
    return list
    
    
    
def get_device_health(token,dnac_ip):

    #requests.packages.urllib3.disable_warnings()
    url = "{}/dna/intent/api/v1/network-health".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    print(response)
    data1 = response.json()['response']
    url = "{}/dna/intent/api/v1/client-health".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    data = response.json()['response'][0]["scoreDetail"]
    list = [['totalCount','goodCount','unmonCount','fairCount','badCount'
            ,'总客户数量','有线连接数量','无线连接数量'
            ,'有线连接质量差的数量','有线连接质量良好的数量','有线连接质量优良的数量'
            ,'无线连接质量差的数量','无线连接质量良好的数量','无线连接质量优良的数量']]
    list.append([data1[0]["totalCount"],data1[0]["goodCount"],data1[0]["unmonCount"],data1[0]["fairCount"],data1[0]["badCount"]
                ,data[0]["clientCount"],data[1]["clientCount"],data[2]["clientCount"]
                ,data[1]["scoreList"][0]["clientCount"],data[1]["scoreList"][1]["clientCount"],data[1]["scoreList"][2]["clientCount"]
                ,data[2]["scoreList"][0]["clientCount"],data[2]["scoreList"][1]["clientCount"],data[2]["scoreList"][2]["clientCount"]])
    return list
    
    

def get_device_health_table(token,dnac_ip):

    #requests.packages.urllib3.disable_warnings()
    url = "{}/dna/intent/api/v1/network-health".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    data = response.json()['response']
    list = [['goodCount','unmonCount','fairCount','badCount']]
    list.append([data[0]["goodCount"],data[0]["unmonCount"],data[0]["fairCount"],data[0]["badCount"]])
    return list

def get_table_data_3(token,dnac_ip):
    list = []
    list.append(get_device_type(token,dnac_ip))
    list.append(get_device_software(token,dnac_ip))
    list.append(get_device_health_table(token,dnac_ip))
    return list
    
def get_tasks(token,dnac_ip):

    #requests.packages.urllib3.disable_warnings()
    url = "{}/dna/intent/api/v1/task".format(dnac_ip)
    response = requests.get(url, headers={
              'content-type': "application/json",
              'x-auth-token': token
          }, verify=False)
    data = response.json()
    list = [['instanceTenantId','id','version','serviceType','isError']]
    for item in data['response']:
        print(json.dumps(item,sort_keys=True,indent=4))
        list.append([item["instanceTenantId"],item["id"],item["version"],item["serviceType"],item["isError"]])
    print(list)
    return list


    