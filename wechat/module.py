# -*- coding: utf-8 -*-


class Client:
    def __init__(self, client_json):
        self.__dict__ = client_json
        self.flows = []  # collection of Flow object


class Flow:
    def __init__(self, flow_json):
        self.__dict__ = flow_json


class DatasetItem:
    def __init__(self):
        self.flows_per_day = []  # collection of Flow object of one day
        self.ts = ""
        self.device_id = ""
        self.device_name = ""
        self.device_ip = ""
        self.device_mac = ""
        self.recentDeviceMac = ""
        self.ssid = None
        self.ap_name = None
        self.application_num = 0
        self.destination_num = 0
        self.sent_sum = 0
        self.sent_avg = 0.
        self.recv_sum = 0
        self.recv_avg = 0.
        self.flows_sum = 0
        self.flows_avg = 0.
        self.protocol_num = 0
        self.port_num = 0
        self.activeSeconds_sum = 0
        self.activeSeconds_avg = 0.
        self.label = 0
