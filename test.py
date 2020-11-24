import time
from gevent import monkey
from gevent.pywsgi import WSGIServer
import requests
import requests,json
from requests.auth import HTTPBasicAuth
from datetime import timedelta
import urllib3
urllib3.disable_warnings()


requests.adapters.DEFAULT_RETRIES = 50  
s = requests.session()
s.keep_alive = False
# Authentication
BASE_URL = 'https://10.14.40.220' # Example BASE_URL = 'https://sandboxdnac.cisco.com'
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = 'admin' # Example USERNAME = 'devnetuser'
PASSWORD = 'Dnac123!' # Example PASSWORD = 'Cisco123!'

# 下面这句不加也能启动服务，但是你会发现Flask还是单线程，在一个请求未返回时，其他请求也会阻塞，所以请添加这句
#monkey.patch_all()
# gevent end
from flask import Flask, render_template, request, jsonify,redirect,url_for
from flask_cors import CORS
import cisico_api as cc
#全局变量
import define
from collections import Counter
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #解决中文乱码

app = Flask(__name__)

app.jinja_env.auto_reload=True
app.config['TEMPLATES_AUTO_RELOAD']=True
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.send_file_max_age_default = timedelta(seconds=1)

#允许跨域
CORS(app, suppors_credentials=True, resources={r'/*'})


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



def get_dnac_jwt_token():
    print(BASE_URL + AUTH_URL)
    response = requests.post(BASE_URL + AUTH_URL,
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             verify=False, timeout=3).json()
    print(response)
    token = response['Token']
    return token
    
    
token = get_dnac_jwt_token()
# Get list of sites
def get_sites(headers):
    response = requests.get(BASE_URL + SITE_URL,
                            headers=headers, verify=False)
    return response.json()['response']


# Get device by serial
def get_device_by_serial(headers, serial_number):
    response = requests.get(BASE_URL + DEVICES_BY_SERIAL_URL.format(serial_number=serial_number),
                            headers=headers,
                            verify=False)
    return response.json()['response']


# Add devices to site
def add_devices_site(headers, site_id, devices):
    headers['__runsync'] = 'true'
    headers['__runsynctimeout'] = '30'
    response = requests.post(BASE_URL + SITE_DEVICE_URL.format(site_id=site_id),
                             headers=headers, json=devices,
                             verify=False)
    return response.json()


# Create template configuration project
def create_network(headers, site_id, network):
    response = requests.post(BASE_URL + NETWORK_URL.format(site_id=site_id),
                             headers=headers, json=network,
                             verify=False)
    return response.json()


# Get template configuration project
def get_configuration_template_project(headers):
    response = requests.get(BASE_URL + TEMPLATE_PROJECT_URL,
                            headers=headers,
                            verify=False)
    return response.json()


# Create template
def create_configuration_template(headers, project_id, template):
    response = requests.post(BASE_URL + TEMPLATE_URL.format(project_id=project_id),
                             headers=headers, json=template,
                             verify=False)
    return response.json()['response']


# Create configuration template version
def create_configuration_template_version(headers, template_version):
    response = requests.post(BASE_URL + TEMPLATE_VERSION_URL,
                             headers=headers, json=template_version,
                             verify=False)
    return response.json()['response']


# Deploy template
def deploy_configuration_template(headers, deployment_info):
    response = requests.post(BASE_URL + TEMPLATE_DEPLOY_URL,
                             headers=headers, json=deployment_info,
                             verify=False)
    return response.json()


# Get Task result
def get_task(headers, task_id):
    response = requests.get(BASE_URL + TASK_BY_ID_URL.format(task_id=task_id),
                            headers=headers, verify=False)
    return response.json()['response']


# 返回模板列表
def get_template_list():
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = requests.get(BASE_URL + GET_TEMPLEATE_LIST, headers=headers, verify=False).json()
    # print(json.dumps(response,sort_keys=True,indent=4))
    return response


# 返回模板名称列表
def get_template_name_list():
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = requests.get(BASE_URL + GET_TEMPLEATE_LIST, headers=headers, verify=False).json()
    print(json.dumps(response, sort_keys=True, indent=4))
    template_name_list = []
    for template in response:
        template_name_list.append(template['name'])
    # print(template_name_list)
    return template_name_list


# 返回站点列表
def get_site_list():
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = get_sites(headers)
    site_list = [['globalName','level','id']]
    for site in response:
        site_list.append([site['name'],site['siteNameHierarchy'],site['id']])
    #print(site_list)
    return site_list


# 返回站点的名称列表
def get_site_name_list():
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    response = get_sites(headers)
    print(response)
    site_name_list = []
    for site in response:
        site_name_list.append(site['siteNameHierarchy'])
    print(site_name_list)
    return site_name_list


# 为设备配置配置，并且修改设备所属的站点进行网络配置。
# 需要1.site_name（站点名称） 2.serial_number(网络设备序列号) 3.dhcpServerIP（DHCP服务器IP）
#    4.domainName（DNS服务器域名） 5.dnsServerIP（DNS服务器IP） 6.syslogServerIP（系统日志服务器IP）7.template_name(模板名称)

def device_provisioning(site_name, serial_number, dhcpServerIP, domainName, dnsServerIP, syslogServerIP, template_name):
    # obtain the Cisco DNA Center Auth Token
    token = get_dnac_jwt_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}

    # Get Site ID
    # site_name = 'DNA Center Guide Building'
    response = get_sites(headers)
    for site in response:
        if site['name'] == site_name:
            site_id = site['id']

    # print('Printing site name "{site_name}" site id {site_id}'.format(site_name=site_name,
    #                                                                  site_id=site_id))

    # Get Device IP and Name using Serial Number
    # serial_number = '919L3GOS8QC'
    response = get_device_by_serial(headers, serial_number)
    # print(json.dumps(response,sort_keys=True,indent=4))
    if not "managementIpAddress" in response:
        return response['detail']
    device_ip = response['managementIpAddress']
    device_name = response['hostname']
    # print('device name:{device_name}'.format(device_name = dhcpServerIP))
    device_ips = [device_ip]

    # print('\nPrinting device serial {serial_number} device IP {ip}'.format(serial_number=serial_number,
    #                                                                       ip=device_ip))
    # Create Site Network
    network = {
        "settings": {
            "dhcpServer": [
                dhcpServerIP
            ],
            "dnsServer": {
                "domainName": domainName,
                "primaryIpAddress": dnsServerIP
            },
            "syslogServer": {
                "ipAddresses": [
                    syslogServerIP
                ],
                "configureDnacIP": True
            }
        }
    }
    response = create_network(headers, site_id, network)

    site_devices = {
        'device': device_ips
    }

    # Assign device to site
    response = add_devices_site(headers, site_id, site_devices)
    # print(json.dumps(response,sort_keys=True,indent=4))

    # Get Project information
    project_name = "Onboarding Configuration"
    response = get_configuration_template_project(headers)
    project_id = ''
    for project in response:
        if project['name'] == project_name:
            project_id = project['id']
    # 根据模板列表，获取模板的ID
    response = get_template_list()
    for template in response:
        if template['name'] == template_name:
            template_id = template['templateId']

    # Deploy Template to device
    deployment_info = {
        "forcePushTemplate": False,
        "isComposite": False,
        "targetInfo": [
            {
                "hostName": device_name,
                "params": {
                    "permitACLName": "GUIDE-ALLOW-ACL",
                    "denyACLName": "GUIDE-DENY-ACL"
                },
                "type": "MANAGED_DEVICE_IP"
            }
        ],
        "templateId": template_id
    }
    response = deploy_configuration_template(headers, deployment_info)
    # print(json.dumps(response['deploymentId'],sort_keys=True,indent=4))
    return response['deploymentId']


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
    # print(json.dumps(data,sort_keys=True,indent=4))
    device_serialNumber_list = []
    for item in data['response']:
        #    print(json.dumps(item,sort_keys=True,indent=4))
        #    if(item['serialNumber'] != null):
        device_serialNumber_list.append([item["hostname"], item['serialNumber']])
    # print(device_serialNumber_list)
    return device_serialNumber_list

@app.route('/link_network',methods=['GET','POST'])
def link_network():
    if request.method=='GET':
        print("get")
        return render_template('index.html')
    address=request.form.get('access_address')
    name=request.form.get('username')
    password=request.form.get('password')
    token = requests.post(address + AUTH_URL,
                             auth=HTTPBasicAuth(name, password),
                             headers={'Connection': 'close','content-type': 'application/json'},
                             verify=False, timeout=3).json()
    print(address,name,password)

    global BASE_URL
    global USERNAME
    global PASSWORD
    BASE_URL = address
    accessAddress=address
    USERNAME = name
    PASSWORD = password
    #change_Authentication(BASE_URL, USERNAME,PASSWORD)
    response = requests.post(BASE_URL + AUTH_URL,
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             headers={'Connection': 'close','content-type': 'application/json'},
                             verify=False, timeout=3).json()
    if "Token" in response:
        return render_template('index.html',msg='连接成功')
    return render_template('index.html',msg='连接失败')
    '''例子
    if address=='192.168.1.0' and name=='123' and password=='123':
        print("well")
        return render_template('index.html',msg='success')
        #return render_template('index.html',msg='success')
    
    token = cc.get_token(address, name, password)
    print(token)
    if ("Token" in token.keys()):
        state = 1  # 连接成功
        return ("false")
    else:
        state = 0  # 连接失败
        return ("true")
    '''

@app.route('/task',methods=['POST','GET'])
def task():
    if request.method == 'GET':
        setTable = cc.get_tasks(token, BASE_URL)
        '''
        setTable = [
            ['Progress', 'Root Id', 'Start Time', 'Service Type', 'Is Error'],

            ['Cisco_69:e9:02', 'AIR-CT3504-K9', '00:72:78:69:e9:00', 'Cisco Controller','16.6.4'],

            ['leaf1.abc.inc', 'C9300-24UX', 'f8:7b:20:53:f0:80', 'IOS-XE', '16.6.5'],

            ['leaf2.abc.inc', 'C9300-24UX', 'f8:7b:20:71:4a:00', 'IOS-XE', '16.6.5'],

            ['spine1.abc.inc', 'WS-C3850-48P-E', 'f8:b7:e2:bf:f2:00', 'IOS-XE', '16.6.5'],

            ['spine1.abc.inc', 'WS-C3850-48P-E', 'f8:b7:ee:bf:f2:00', 'IOS-XE', '16.6.5']
        ]
        '''
        # list转dict

        USER_DICT = {}
        setTable_len=len(setTable)
        if(len(setTable)>11):
            setTable_len=11


        for i in range(setTable_len - 1):
            user_dict = {}
            user_dict[setTable[0][0]] = setTable[i + 1][0]
            user_dict['Root_Id'] = setTable[i + 1][1]
            user_dict['Start_Time'] = setTable[i + 1][2]
            user_dict['Service_Type'] = setTable[i + 1][3]
            user_dict['Is_Error'] = setTable[i + 1][4]
            USER_DICT[i + 1] = user_dict
        '''
        USER_DICT={
            '1':{'Hostname':'Cisco_69:e9:02','Platform_Id':'AIR-CT3504-K9','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco_Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '2':{'Hostname':'leaf1.abc.inc','Platform_Id':'C9300-24UX','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '3':{'Hostname':'leaf2.abc.inc','Platform_Id':'C9300-24UX','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '4':{'Hostname':'spine1.abc.inc','Platform_Id':'WS-C3850-48P-E','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '5':{'Hostname':'spine1.abc.inc','Platform_Id':'WS-C3850-48P-E','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
        }
        '''
        print(USER_DICT)
        return render_template('task.html', user_dict=USER_DICT)

#点击“服务”中的信息查询后响应
@app.route('/information',methods=['GET','POST'])
def information():
    print("well")
    if request.method == 'GET':
        setTable = cc.get_device(token, BASE_URL)
        '''
        setTable=[
            ['Hostname', 'Platform Id', 'MacAddress', 'Software Type', 'Software Version', 'Up Time'],
            ['Cisco_69:e9:02', 'AIR-CT3504-K9', '00:72:78:69:e9:00', 'Cisco Controller', '8.8.111.0', '19 days, 17:20:04.00'],
            ['leaf1.abc.inc', 'C9300-24UX', 'f8:7b:20:53:f0:80', 'IOS-XE', '16.6.5', '19 days, 18:43:02.24'],
            ['leaf2.abc.inc', 'C9300-24UX', 'f8:7b:20:71:4a:00', 'IOS-XE', '16.6.5', '19 days, 18:43:51.51'],
            ['spine1.abc.inc', 'WS-C3850-48P-E', 'f8:b7:e2:bf:f2:00', 'IOS-XE', '16.6.5', '13 days, 19:14:32.31'],
            ['spine1.abc.inc', 'WS-C3850-48P-E', 'f8:b7:e2:bf:f2:00', 'IOS-XE', '16.6.5', '13 days, 19:14:32.31']
        ]
        '''
        #list转dict
        USER_DICT={}
        for i in range(len(setTable)-1):
            user_dict = {}
            user_dict[setTable[0][0]]=setTable[i+1][0]
            user_dict['Platform_Id']=setTable[i+1][1]
            user_dict[setTable[0][2]]=setTable[i+1][2]
            user_dict['Software_Type']=setTable[i+1][3]
            user_dict['Software_Version']=setTable[i+1][4]
            user_dict['Up_Time']=setTable[i][5]
            USER_DICT[i+1]=user_dict
        '''
        USER_DICT={
            '1':{'Hostname':'Cisco_69:e9:02','Platform_Id':'AIR-CT3504-K9','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco_Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '2':{'Hostname':'leaf1.abc.inc','Platform_Id':'C9300-24UX','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '3':{'Hostname':'leaf2.abc.inc','Platform_Id':'C9300-24UX','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '4':{'Hostname':'spine1.abc.inc','Platform_Id':'WS-C3850-48P-E','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
            '5':{'Hostname':'spine1.abc.inc','Platform_Id':'WS-C3850-48P-E','MacAddress':'00:72:78:69:e9:00','Software_Type':'Cisco Controller','Software_Version':'8.8.111.0','Up_Time':'19 days, 17:20:04.00'},
        }
        '''
        print(USER_DICT)
        return render_template('information.html',user_dict=USER_DICT)

#诊断
@app.route('/dignose',methods=['GET','POST'])
def dignose():
    if request.method == 'GET':
        result = cc.get_device_health(token, BASE_URL)
        '''
        result=[
            [],
            [4,0,4,0,0,4,2,2,0,0,2,0,0,2]
        ]
        '''
        # list转dict
        USER_DICT = {
            '1':{'name':'总设备数量','results':result[1][0],'img':'../static/pic/service_img.png'},
            '2':{'name':'普通设备数量','results':result[1][3],'img':'../static/pic/common_img.png'},
            '3':{'name':'未检测到设备数量','results':result[1][2],'img':'../static/pic/umon_img.png'},
            '4':{'name':'健康设备数量','results': result[1][1],'img':'../static/pic/link_img.png'},
            '5':{'name':'异常设备数量','results': result[1][4],'img':'../static/pic/bad_img.png'},
            '6':{'name':'总客户数量','results': result[1][5],'img':'../static/pic/allpeople_img.png'},
            '7':{'name':'有线连接数量','results': result[1][6],'img':'../static/pic/wired_img.png'},
            '8':{'name':'无线连接数量','results': result[1][7],'img':'../static/pic/wireless_img.png'},
            '9':{'name':'有线连接质量差数量','results': result[1][8],'img':'../static/pic/wiredbad_img.png'},
            '10':{'name':'有线连接质量良好数量量','results': result[1][9],'img':'../static/pic/wiredgood_img.png'},
            '11':{'name':'有线连接质量优良的数量','results': result[1][10],'img':'../static/pic/wiredexcellent_img.png'},
            '12':{'name':'无线连接质量差数量','results': result[1][11],'img':'../static/pic/wirelessbad_img.png'},
            '13':{'name':'无线连接质量良好数量','results': result[1][12],'img':'../static/pic/wirelessgood_img.png'},
            '14':{'name':'无线连接质量优良的数量','results': result[1][13],'img':'../static/pic/wirelessexcellent_img.png'},
        }
        print(USER_DICT)
        return render_template('dignose.html', user_dict=USER_DICT)

#设备数据统计
@app.route('/graphic',methods=['GET','POST'])
def graphic():
    print("well")
    if request.method == 'GET':
        setData=cc.get_table_data_3(token,BASE_URL)
        '''
        setData=[
            [
                    ['AIR-CT3504-K9', 'C9300-24UX', 'WS-C3850-48P-E'],
                    [1, 2, 1]
            ],
            [
                    ['AIR-CT3504-K9', 'C9300-24UX', 'WS-C3850-48P-E'],
                    [1, 2, 1]
            ],
            [
                    ['totalCount', 'goodCount', 'unmonCount', 'fairCount', 'badCount'],
                    [4, 0, 4, 0, 0]
            ]
        ]


        '''
    plt.figure(figsize=(15, 12))  # 调节图形大小
    newlabels_1 = setData[0][0]  # 定义标签
    newsizes_1 = setData[0][1]  # 每块值
    labels = []
    sizes = []
    for i in range(len(newsizes_1)):
        if (newsizes_1[i] == 0):
            continue
        else:
            sizes.append(newsizes_1[i])
            labels.append(newlabels_1[i])

    mycolor = ["red", "deepskyblue", "lightgreen", "yellow", "purple", "orange", "white", "yellowgreen", "navajowhite"]
    colors = []
    explode = []
    for i in range(len(sizes)):
        colors.append(mycolor[i])
        explode.append(0.01)
    explode = tuple(explode)
    patches_1, text1_1, text2_1 = plt.pie(sizes,
                                explode=explode,
                                labels=labels,
                                colors=colors,
                                autopct='%3.2f%%',  # 数值保留固定小数位
                                shadow=True,  # 无阴影设置
                                startangle=90,  # 逆时针起始角度设置
                                pctdistance=0.6)  # 数值距圆心半径倍数的距离
    # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
    for t in text1_1:
        t.set_size(24)
    for t in text2_1:
        t.set_size(30)
    # x，y轴刻度设置一致，保证饼图为圆形
    plt.axis('equal')
    plt.savefig('static/images/1.png')
    plt.close()

    newlabels_2 = setData[1][0]  # 定义标签
    newsizes_2 = setData[1][1]  # 每块值
    labels = []
    sizes = []
    for i in range(len(newsizes_2)):
        if (newsizes_2[i] == 0):
            continue
        else:
            sizes.append(newsizes_2[i])
            labels.append(newlabels_2[i])

    mycolor = ["red", "deepskyblue", "lightgreen", "yellow", "purple", "orange", "white", "yellowgreen", "navajowhite"]
    colors = []
    explode = []
    for i in range(len(sizes)):
        colors.append(mycolor[i])
        explode.append(0.01)
    explode = tuple(explode)
    patches_2, text1_2, text2_2 = plt.pie(sizes,
                                explode=explode,
                                labels=labels,
                                colors=colors,
                                autopct='%3.2f%%',  # 数值保留固定小数位
                                shadow=True,  # 无阴影设置
                                startangle=90,  # 逆时针起始角度设置
                                pctdistance=0.6)  # 数值距圆心半径倍数的距离
    # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
    for t in text1_2:
        t.set_size(24)
    for t in text2_2:
        t.set_size(30)
    # x，y轴刻度设置一致，保证饼图为圆形
    plt.axis('equal')
    plt.savefig('static/images/2.png')
    plt.close()

    newlabels_3 = setData[2][0]  # 定义标签
    newsizes_3 = setData[2][1]  # 每块值
    labels = []
    sizes = []
    for i in range(len(newsizes_3)):
        if (newsizes_3[i] == 0):
            continue
        else:
            sizes.append(newsizes_3[i])
            labels.append(newlabels_3[i])

    mycolor = ["red", "deepskyblue", "lightgreen", "yellow", "purple", "orange", "white", "yellowgreen", "navajowhite"]
    colors = []
    explode = []
    for i in range(len(sizes)):
        colors.append(mycolor[i])
        explode.append(0.01)
    explode = tuple(explode)
    patches_3, text1_3, text2_3 = plt.pie(sizes,
                                explode=explode,
                                labels=labels,
                                colors=colors,
                                autopct='%3.2f%%',  # 数值保留固定小数位
                                shadow=True,  # 无阴影设置
                                startangle=90,  # 逆时针起始角度设置
                                pctdistance=0.6)  # 数值距圆心半径倍数的距离
    # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
    for t in text1_3:
        t.set_size(24)
    for t in text2_3:
        t.set_size(30)
    # x，y轴刻度设置一致，保证饼图为圆形
    plt.axis('equal')
    plt.savefig('static/images/3.png')
    plt.close()
    return render_template('graphic.html')

#查看站点信息
@app.route('/site',methods=['GET','POST'])
def site():
    if request.method == 'GET':
        print(BASE_URL)
        setTable = get_site_list()
        print(setTable)
        '''
        setTable=[
            ['globalName','level','id'],
            ['Global', 'Global', '6818b396-1b52-464c-83cb-399aa44e620a'],
            ['yintong', 'Global/CN/JMU/yintong', 'a4817149-8bed-48fa-b551-5763e31bbe6f'],
            ['Floor 4', 'Global/CN/JMU/yintong/Floor 4', 'b5b2f40b-a161-471b-8a31-cdfb978edd88']
        ]
        '''
        #list转dict
        USER_DICT = {}
        for i in range(len(setTable) - 1):
            user_dict = {}
            user_dict[setTable[0][0]] = setTable[i + 1][0]
            user_dict[setTable[0][1]] = setTable[i + 1][1]
            user_dict[setTable[0][2]] = setTable[i + 1][2]
            USER_DICT[i + 1] = user_dict

        print(USER_DICT)
        return render_template('site.html',user_dict=USER_DICT)


#添加网络设备
@app.route('/adddevice',methods=['GET','POST'])
def adddevice():
    
    if request.method=='GET':
        
        setTable=define.PATH

        # list转dict
        USER_DICT = {}
        for i in range(len(setTable)):
            user_dict = {}
            user_dict["path"] = setTable[i][0]
            user_dict["tip"] = setTable[i][1]
            USER_DICT[i] = user_dict

        print(USER_DICT)

        return render_template('add.html', user_dict=USER_DICT)

    site_name = request.form.get('access_address')
    serial_number = request.form.get('username')
    print(request.form)
    print("site_name")
    print(site_name)
    print(serial_number)
    path_list, path_interface_list=get_path_list(site_name,serial_number)
    print(path_list)
    define.PATH = path_interface_list
    print(path_interface_list)
    return redirect('/adddevice')
    

    
import use

if __name__ == '__main__':
    app.run(port=5080)
