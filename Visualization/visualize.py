# Test visualize script
# -*- coding: utf-8 -*-
import json
import argparse
import sys
import plotly

import plotly.graph_objs as go
import plotly.plotly as py
import plotly.offline as plo

import dash
import dash_core_components as dcc
import dash_html_components as html



# types of data objects:
DSOBJECT = 1
DSOBJECTLIST = 2
VMOBJECT = 3
VMOBJECTLIST = 4

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

class DSObject():
    """
    A single datastore object
    """
    def __init__(self, data):
        """
        Initializer
        """
        self.info = data

    def visualize(self):
        """
        Create the visualization
        :return:
        """
        
        # text and graph part
        dsname = self.info[0]['Datastore name']
        capacity = self.info[0]['Capacity']
        provisioned_space = self.info[0]['Provisioned space']
        free_space = self.info[0]['Free space']
        fsp = self.info[0]['Free space percentage']
        
        free_space_per = float(fsp[:-1])
        used = 100 - free_space_per

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        
        app.layout = html.Div(children=[
            html.H1(children='Datastore Properties'),
                                        
            html.Div(children='''
            Dash: A dashboard of datastores.
            '''),
                                        
            dcc.Graph(
                      id='example-graph',
                      figure={
                      'layout': {
                      'title': 'Datastore: ' + dsname + ", Capacity: " + capacity + ", Provisioned Space " + provisioned_space + ", Free Space: " + free_space,
                      'margin': {
                      'l': 50,
                      'r': 50,
                      'b': 100,
                      't': 100
                      }
                      
                      },
                      'data': [
                               {
                               'values': [free_space_per, used],
                               'labels': ['free', 'used'],
                               'type': 'pie'
                               }
                            ]
                      
                      
                      }
                    )
                ])
        app.run_server(host='10.244.105.32', port=9999, debug=True)


class DSObjectList():
    """
    A list of data store objects
    """
    def __init__(self, data):
        """
        Initializer
        """
        self.info = data

    def visualize(self):
        """
        Create the visualization
        :return:
        """

        # text: 'Datastore name', 'Capacity', 'Provisioned space', 'Free space',
        # graph: free space %
        # this is the list of children that will go into the app layout
        children = list()
        title = html.H1(children='Datastore Properties')
        desc = html.Div(children='''
                Dash: A dashboard of datastores.
            ''')
        children.append(title)
        children.append(desc)
        n = 0
        for obj in self.info:
            # text and graph info
            dsname = obj['Datastore name']
            capacity = obj['Capacity']
            provisioned_space = obj['Provisioned space']
            free_space = obj['Free space']

            fsp = obj['Free space percentage']
            free_space_per = float(fsp[:-1])
            used = 100 - free_space_per
            temp = n
            n += 1
            temp = str(temp)
            graph = dcc.Graph(
                id='pie-graph'+temp,
                figure={
                    'data': [
                        {
                            'values': [free_space_per, used],
                             'labels': ['free', 'used'],
                            'type': 'pie'
                        }
                    ],
                    'layout': {
                        'title': 'Datastore: ' + dsname + ", Capacity: " + capacity + ", Provisioned Space " + provisioned_space + ", Free Space: " + free_space,
                        'margin': {
                              'l': 50,
                              'r': 50,
                              'b': 100,
                              't': 100
                              }

                    }
                }
            )
            children.append(graph)

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        app.layout = html.Div(children=children)
        app.run_server(host='10.244.105.32', port=9999,debug=True)

class VMPropObject():
    """
    A single VM's properties object
    """
    def __init__(self, data):
        """
        Initializer
        """
        self.info = data

    def visualize(self):
        """
        Create the visualization
        :return:
        """
            # text and graph part
        name = self.info[0]['Name']
        last_booted = self.info[0]['Last Booted On']
        res_cpu = self.info[0]['Reserved CPU']
        mem_use = self.info[0]['Current Memory Usage']
        mem = float((mem_use.split())[0])
        guest_os = self.info[0]['Guest OS']
        ds_free = self.info[0]['DS Free Space']
        total_mem = self.info[0]['Total Memory']
        powerstate = self.info[0]['Powerstate']
        uuid = self.info[0]['UUID']
        ds_cap = self.info[0]['DS Capacity']
        cpu_use = self.info[0]['Current CPU Usage']
        curr_cpu_use = int((cpu_use.split())[0])
        ds_free_per = self.info[0]['DS Free Percentage']
        host = self.info[0]['Host']
        path = self.info[0]['Path to VM']
        dsname = self.info[0]['Datastore Name']
            
            # networks = self.info[0]['VM Networks']
            
        free_space_per = float(ds_free_per[:-1])
        used = 100 - free_space_per
        
        
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
                                            
        app.layout = html.Div(children=[
        html.H1(children='Virtual Machine Properties'),
                                        
        html.Div(children='''
                Dash: Properties of a single VM.
                '''),
                                        
        dcc.Markdown("""
            VM Properties:
            ------------------------
            VM Name: {}
            Last booted: {}
            Reserved CPU: {}
            Current memory usage: {}
            Guest OS: {} 
            DS Free Space: {}
            Total Memory: {} 
            Powerstate: {}
            UUID: {}
            DS Capacity: {}
            Current CPU Usage: {}
            DS Free Percentage: {}
            Host: {}
            Path to VM: {}
            Datastore name: {}
                    """.format(name, last_booted, res_cpu, mem_use, guest_os, ds_free, total_mem, powerstate, uuid, ds_cap, cpu_use, ds_free_per, host, path, dsname)),
                                                                            
        dcc.Graph(
                          id='vm-single-graph',
                          figure={
                            'data': [
                             {
                             'values': [free_space_per, used],
                            'labels': ['free', 'used'],
                            
                            'type': 'pie'
                            }
                            ],
                                                                                      
                        'layout': {
                        'title': 'Free vs.Used space for Datastore: ' + dsname,
                  'legend': {'x': 0, 'y': 1}
                  
                  
                  }
                  
                            }
                        ),
        dcc. Graph(
                        id='vm-single-graph2',
                           figure={
                           'data': [
                                    {'x': ["CPU (in MHz)", "Memory (in MB)"], 'y': [curr_cpu_use, mem], 'type': 'bar', 'name': 'CPU & Mem'},
                                    
                           ]
                           }
                        )
                        ])
        app.run_server(host='10.244.105.32', port=9999, debug=True)
    





class VMPropObjectList():
    """
    A list of VM's properties objects
    """
    def __init__(self, data):
        """
        Initializer
        """
        self.info = data

    def visualize(self):
        """
        Create the visualization
        :return:
        """
        # text: 'Datastore name', 'Capacity', 'Provisioned space', 'Free space',
        # graph: free space %
        # this is the list of children that will go into the app layout
        children = list()
        title = html.H1(children='VM Properties')
        desc = html.Div(children='''
                    Dash: A dashboard of VM Properties.
                        ''')
        children.append(title)
        children.append(desc)
        n = 0
        for obj in self.info:
            # text and graph info
            # text and graph part
            name = self.info[0]['Name']
            last_booted = self.info[0]['Last Booted On']
            res_cpu = self.info[0]['Reserved CPU']
            mem_use = self.info[0]['Current Memory Usage']
            mem = float((mem_use.split())[0])
            guest_os = self.info[0]['Guest OS']
            ds_free = self.info[0]['DS Free Space']
            total_mem = self.info[0]['Total Memory']
            powerstate = self.info[0]['Powerstate']
            uuid = self.info[0]['UUID']
            ds_cap = self.info[0]['DS Capacity']
            cpu_use = self.info[0]['Current CPU Usage']
            curr_cpu_use = int((cpu_use.split())[0])
            ds_free_per = self.info[0]['DS Free Percentage']
            host = self.info[0]['Host']
            path = self.info[0]['Path to VM']
            dsname = self.info[0]['Datastore Name']
            
            free_space_per = float(ds_free_per[:-1])
            used = 100 - free_space_per

            temp = n
            n += 1
            temp = str(temp)
            
            text = dcc.Markdown("""
                VM Properties:
                ------------------------
                VM Name: {}
                Last booted: {}
                Reserved CPU: {}
                Current memory usage: {}
                Guest OS: {}
                DS Free Space: {}
                Total Memory: {}
                Powerstate: {}
                UUID: {}
                DS Capacity: {}
                Current CPU Usage: {}
                DS Free Percentage: {}
                Host: {}
                Path to VM: {}
                Datastore name: {}
                """.format(name, last_booted, res_cpu, mem_use, guest_os, ds_free, total_mem, powerstate, uuid, ds_cap, cpu_use, ds_free_per, host, path, dsname))
            children.append(text)
            
            graph = dcc.Graph(
                        id='vm-single-graph'+temp,
                            figure={
                                'data': [
                                    {
                                               'values': [free_space_per, used],
                                               'labels': ['free', 'used'],
                                               
                                               'type': 'pie'
                                               }
                                               ],
                                      
                                      'layout': {
                                      'title': 'Free vs.Used space for Datastore: ' + dsname,
                                      'legend': {'x': 0, 'y': 1}
                                      
                                      
                                      }
                                      
                                      }
                                      )
            children.append(graph)
                                                                                            
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
                                                                                                
        app.layout = html.Div(children=children)
        app.run_server(host='10.244.105.32', port=9999, debug=True)




class BundleObject():
    """
    A Bundle Object is the classification of BPC data input received by this script.
    """

    DSOBJECT_KEYS = 'Datastore name'
    #['Datastore name', 'Capacity', 'Provisioned space', 'Free space', 'Free space percentage']
    VMPROPERTIESOBJ_KEYS = 'Name'
    #['Name', 'Last Booted On', 'Reserved CPU', 'Current Memory Usage', 'Guest OS', 'DS Free Space', 'Total Memory', 'Powerstate', 'UUID', 'DS Capacity', 'Current CPU Usage', 'DS Free Percentage', 'Host', 'Path to VM', 'Datastore Name']

    def __init__(self, bundle_args):
        """
        Initialize a bundle object.
        :param bundle_args: a string which represents a list of bundle information in json format, where each
        json represents a bundle. For example:

        bundle_args = [
            {
            Datastore name:  "BCL-NFS-VOL-SHARED-001",
            Capacity:  "1.0 TiB",
            Provisioned space:  "649.7 GiB",
            Free space:  "896.8 GiB",
            Free space percentage: "87.5752735883%",
            }
        ]
        """
        self.data = json.loads(bundle_args)


    def find_input_type(self):
        """
        Find the type of input data received and create that object
        :return:
        """

        try:
            
            if BundleObject.DSOBJECT_KEYS in str(self.data[0].keys()):
                if len(self.data) == 1:
                    d = DSObject(self.data)
                    
                    return d
                else:
                    d = DSObjectList(self.data)
                    return d

            elif BundleObject.VMPROPERTIESOBJ_KEYS in str(self.data[0].keys()):
                if len(self.data) == 1:
                    v = VMPropObject(self.data)
                    return v
                else:
                    v = VMPropObjectList(self.data)
                    return v

        except IOError:
            raise RuntimeError("IO Error find input type")


def main():
    parser = argparse.ArgumentParser()

    # pass a list of bundles
    parser.add_argument('-b', metavar='<bundle>')

    args = parser.parse_args()

    data_input = BundleObject(args.b)
    
    data_obj_type = data_input.find_input_type()

    data_obj_type.visualize()

if __name__ == "__main__":
    main()

