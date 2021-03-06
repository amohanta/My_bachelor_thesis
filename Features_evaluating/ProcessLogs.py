"""
This file goes into logs file and creates "connection 4-tuples" objects.
"""
from PrintManager import __PrintManager__
from EvaluateData import EvaluateData
from Connection_4_tuple import Connection4tuple
# This class, there are all methods for proccessing LogFiles.


class ProcessLogs(EvaluateData):
    def __init__(self, name_of_result):
        super(ProcessLogs, self).__init__()
        self.infected_ips_list = None
        self.conn_log = None
        self.name_of_result = name_of_result

    def set_infected_ips(self, infected_ips_list):
        self.infected_ips_list = infected_ips_list

    def evaluate_features(self, path_to_dataset):
        self.evaluate_conn_file(path_to_dataset)
        self.evaluate_ssl_file(path_to_dataset)

    # This method process con.log file.
    # It works inside the opened file, because of large files (such as 70Gb)
    def evaluate_conn_file(self, path_to_dataset):
        __PrintManager__.processLog_evaluating()
        with open(path_to_dataset + '\\bro\\conn.log') as f:
            # go thru file line by line and evaluate each line (line is flow)
            for line in f:
                if '#' in line:
                    continue
                split = line.split('	')
                # 2-srcIpAddress, 4-dstIpAddress, 5-dstPort, 6-Protocol
                connection_index = split[2], split[4], split[5], split[6]
                ipaddresses = split[2], split[4]

                if connection_index not in self.connection_4_tuples.keys():
                    self.connection_4_tuples[connection_index] = Connection4tuple(connection_index)

                if ipaddresses in self.infected_ips_list:
                    self.connection_4_tuples[connection_index].add_flow(line, "MALWARE")
                else:
                    self.connection_4_tuples[connection_index].add_flow(line, "NORMAL")

        f.close()

    def evaluate_ssl_file(self, path_to_dataset):
        number_adding_ssl = 0
        __PrintManager__.processLog_evaluate_ssl()
        try:
            with open(path_to_dataset + "\\bro\\ssl.log") as f:
                # go thru ssl file line by line and for each ssl line check all uid of flows
                for line in f:
                    if '#' in line:
                        continue
                    split = line.split('	')
                    ssl_uid = split[1]

                    for key in self.connection_4_tuples.keys():
                        if ssl_uid in self.connection_4_tuples[key].get_uid_flow_list():
                            self.connection_4_tuples[key].add_ssl_log(line)
                            number_adding_ssl += 1
            f.close()
        except IOError:
            __PrintManager__.processLog_no_ssl_logs()

        __PrintManager__.processLog_number_of_addes_ssl(number_adding_ssl)

    def print_connection_4_tuple(self):
        for key in self.connection_4_tuples.keys():
            self.connection_4_tuples[key].print_features()

    # This method checks error in connection 4-tuple.
    # So if 4-tuple contains some malware flows and some normal flow, that is error!!!
    def check_4_tuples(self):
        __PrintManager__.processLog_check_tuples()
        no_variants = 0
        for key in self.connection_4_tuples.keys():
            if self.connection_4_tuples[key].get_malware_label() != 0 and \
                            self.connection_4_tuples[key].get_normal_label() != 0:
                    print "Tuple index: ", self.connection_4_tuples[key].tuple_index
                    print "Number of malware: ", self.connection_4_tuples[key].get_malware_label()
                    print "Number of normal: ", self.connection_4_tuples[key].get_normal_label()
                    no_variants += 1

        if no_variants == 0:
            __PrintManager__.processLog_result_1_of_check()
        else:
            __PrintManager__.processLog_result_2_of_check()
