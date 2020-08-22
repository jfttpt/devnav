# -*- coding: utf-8 -*-

from . import module
import json
import csv
from collections import namedtuple
import pandas as pd
from sklearn.model_selection import train_test_split
from datetime import date, timedelta
from dateutil import parser
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib
import meraki
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


def show_device_data(device_id, dashboard):
    client_traffic = dashboard.networks.getNetworkClientTrafficHistory('L_851180329573037342', device_id)
    dump = json.dumps(client_traffic, indent=4)
    print(dump)
    df = pd.read_json(dump)
    print(df)
    df.to_csv(device_id + '.csv')


def load_dataset(cv_file, columns):
    df_ori = pd.read_csv(cv_file)
    print(df_ori)
    df = df_ori[columns]
    print(df)
    X = df.drop('label', axis=1)
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.50, random_state=2020, stratify=y)
    return X_train, X_test, y_train, y_test


def create_dataset(clients, devices, dashboard):
    dataset_items = []
    for client_data in clients:
        client = module.Client(client_data)
        client_traffic = dashboard.networks.getNetworkClientTrafficHistory('L_851180329573037342', client.id)
        client_dataset_items = set_dateset_item_basic(client, devices, client_traffic)
        set_dataset_item_advance(client_dataset_items)
        dataset_items.extend(client_dataset_items)
    return dataset_items


def set_dateset_item_basic(client, devices, client_traffic):
    client_dataset_items = []
    for flow_data in client_traffic:
        flow = module.Flow(flow_data)
        client.flows.append(flow)
        if flow.ts not in [dataset_item.ts for dataset_item in client_dataset_items]:
            dataset_item = module.DatasetItem()
            dataset_item.ts = flow.ts
            dataset_item.device_id = client.id
            dataset_item.device_name = client.description
            dataset_item.device_ip = client.ip
            dataset_item.device_mac = client.mac
            dataset_item.recentDeviceMac = client.recentDeviceMac
            dataset_item.ssid = client.ssid
            if client.ssid is not None:
                for device in devices:
                    if device.get('mac', None) == client.recentDeviceMac:
                        dataset_item.ap_name = device.get('name', None)
            if 'Camera' in dataset_item.device_name:
                dataset_item.label = 1
            dataset_item.flows_per_day.append(flow)
            client_dataset_items.append(dataset_item)
        else:
            for dataset_item in client_dataset_items:
                if flow.ts == dataset_item.ts:
                    dataset_item.flows_per_day.append(flow)
                    continue

    print(client.description, len(client.flows), len(client_dataset_items))
    return client_dataset_items


def set_dataset_item_advance(client_dataset_items):
    application_set = set()
    destination_set = set()
    protocol_set = set()
    port_set = set()
    for dataset_item in client_dataset_items:
        for flow in dataset_item.flows_per_day:
            dataset_item.flows_sum += flow.numFlows
            dataset_item.recv_sum += flow.recv
            dataset_item.sent_sum += flow.sent
            dataset_item.activeSeconds_sum += flow.activeSeconds
            application_set.add(flow.application)
            destination_set.add(flow.destination)
            protocol_set.add(flow.protocol)
            port_set.add(flow.port)
        dataset_item.application_num = len(application_set)
        dataset_item.destination_num = len(destination_set)
        dataset_item.protocol_num = len(protocol_set)
        dataset_item.port_num = len(port_set)
        dataset_item.recv_avg = dataset_item.recv_sum / len(dataset_item.flows_per_day)
        dataset_item.sent_avg = dataset_item.sent_sum / len(dataset_item.flows_per_day)
        dataset_item.flows_avg = dataset_item.flows_sum / len(dataset_item.flows_per_day)
        dataset_item.activeSeconds_avg = dataset_item.activeSeconds_sum / len(dataset_item.flows_per_day)
        # print(dataset_item.ts, dataset_item.device_name, dataset_item.device_id, dataset_item.flows_num)


def write_dataset_csv(filename, dataset_items):
    feature = namedtuple('feature', ['ts', 'device_id', 'device_name', 'device_ip', 'device_mac', 'recentDeviceMac',
                                     'ssid', 'ap_name',
                                     'application_num', 'destination_num', 'sent_sum', 'sent_avg', 'recv_sum',
                                     'recv_avg', 'flows_sum', 'flows_avg', 'protocol_num', 'port_num',
                                     'activeSeconds_sum', 'activeSeconds_avg',
                                     'label'])
    with open(filename, 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(feature._fields)  # namedtuple breaks convention public fields have single underscore
        for dataset_item in dataset_items:
            writer.writerow([dataset_item.ts, dataset_item.device_id, dataset_item.device_name, dataset_item.device_ip,
                             dataset_item.device_mac, dataset_item.recentDeviceMac, dataset_item.ssid,
                             dataset_item.ap_name, dataset_item.application_num, dataset_item.destination_num,
                             dataset_item.sent_sum, dataset_item.sent_avg, dataset_item.recv_sum, dataset_item.recv_avg,
                             dataset_item.flows_sum, dataset_item.flows_avg, dataset_item.protocol_num,
                             dataset_item.port_num, dataset_item.activeSeconds_sum, dataset_item.activeSeconds_avg,
                             dataset_item.label])


def get_previous_day_dataset(dataset_items, day):
    previous_day_dataset_items = []
    previous_day = day - timedelta(days=1)
    for dataset_item in dataset_items:
        # timestamp = datetime.fromisoformat(dataset_item.ts[:-1])  # python3.7+ support fromisoformat
        timestamp = parser.isoparse(dataset_item.ts[:-1])
        if timestamp.date() == previous_day:
            previous_day_dataset_items.append(dataset_item)

    return previous_day_dataset_items


# def find_camera(cv_file):
#     columns = ['application_num', 'destination_num', 'sent_sum', 'sent_avg', 'recv_sum', 'recv_avg',
#                'flows_sum', 'flows_avg', 'protocol_num', 'port_num', 'activeSeconds_sum', 'activeSeconds_avg',
#                'label']
#
#     df = pd.read_csv(cv_file)[columns]
#     X_test = df.drop('label', axis=1)
#     y_test = df['label']
#
#     ss = StandardScaler()
#     X_test_scaled = ss.fit_transform(X_test)
#     y_test = np.array(y_test)
#     print(y_test)
#
#     rfc = joblib.load('save/rfc3.pkl')
#     print(rfc.predict(X_test_scaled))


def find_camera_from_dataset(dataset_items):
    data_x_lists = []
    data_y_lists = []
    for dataset_item in dataset_items:
        data_x_lists.append([dataset_item.application_num, dataset_item.destination_num, dataset_item.sent_sum,
                             dataset_item.sent_avg, dataset_item.recv_sum, dataset_item.recv_avg,
                             dataset_item.flows_sum, dataset_item.flows_avg, dataset_item.protocol_num,
                             dataset_item.port_num, dataset_item.activeSeconds_sum, dataset_item.activeSeconds_avg])
        data_y_lists.append([dataset_item.label])

    columns = ['application_num', 'destination_num', 'sent_sum', 'sent_avg', 'recv_sum', 'recv_avg',
               'flows_sum', 'flows_avg', 'protocol_num', 'port_num', 'activeSeconds_sum', 'activeSeconds_avg']

    X_test = pd.DataFrame(data_x_lists, columns=columns)
    y_test = pd.DataFrame(data_y_lists, columns=['label'])
    scaler_file = os.path.join(BASE_DIR, "wechat/save/std_scaler.bin")
    ss = joblib.load(scaler_file)
    X_test_scaled = ss.transform(X_test)
    y_test = np.array(y_test)
    model_file = os.path.join(BASE_DIR, "wechat/save/rfc11.pkl")
    rfc = joblib.load(model_file)
    y_hats = rfc.predict(X_test_scaled)
    print(y_hats)
    print(classification_report(y_hats, y_test))
    camera_items = [dataset_items[i] for i in range(len(y_hats)) if y_hats[i] == 1]
    for camera_item in camera_items:
        print(camera_item.ts, camera_item.ap_name, camera_item.device_name, camera_item.device_ip)

    return camera_items


def find_camera_from_meraki():
    API_KEY = "e0434bdb39fb505c9862e8f23aef5292b138afd8"
    BASE_URL = "https://api.meraki.cn/api/v1"

    dashboard = meraki.DashboardAPI(API_KEY, BASE_URL, suppress_logging=True)
    clients = dashboard.networks.getNetworkClients('L_851180329573037342')
    devices = dashboard.networks.getNetworkDevices('L_851180329573037342')
    print(clients)

    dataset_items = create_dataset(clients, devices, dashboard)

    # filename = "dataset.csv"
    # write_dataset_csv(filename, dataset_items)

    today = date.today()
    previous_day_dataset_items = get_previous_day_dataset(dataset_items, today)

    # filename = "dataset_new.csv"
    # write_dataset_csv(filename, previous_day_dataset_items)

    # find_camera(filename)
    cameras = find_camera_from_dataset(previous_day_dataset_items)
    # find_camera(dataset_items)

    return cameras
