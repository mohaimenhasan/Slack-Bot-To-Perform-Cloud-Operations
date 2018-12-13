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

        labels = ['Used', 'Free']
        str = self.info[0]['Free space percentage']
        free = float(str[:-1])
        used = 100 - free
        dsname = self.info[0]['Datastore name']

        values = [used, free]
        """
        # create trace
        trace = go.Pie(labels=labels, values=values, name="Datastore Information for " + dsname)
        # pack data
        data = [trace]
        plo.plot(data, filename='simple_pie.html')
        print("success!")
        """
        trace = go.Pie(labels=labels, values=values, name="Datastore Information for " + dsname)
        trace1 = go.Scatter(
            x=[0, 1, 2, 3, 4, 5, 6, 7, 8],
            y=[0, 1, 2, 3, 4, 5, 6, 7, 8],
            name='Name of Trace 1'
        )
        trace2 = go.Scatter(
            x=[0, 1, 2, 3, 4, 5, 6, 7, 8],
            y=[1, 0, 3, 2, 5, 4, 7, 6, 8],
            name='Name of Trace 2'
        )
        data = [trace, trace1, trace2]
        layout = go.Layout(
            title='Datastore information',
            xaxis=dict(
                title='x Axis',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title='y Axis',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )
        fig = go.Figure(data=data, layout=layout)
        plo.plot(fig, filename='simple_pie.html')


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
                Dash: A web application framework for Python.
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
                            'type': 'pie'
                        }
                    ],
                    'layout': {
                        'title': 'Datastore: ' + dsname + " Cap: " + capacity + "ProvSpace " + provisioned_space

                    }
                }
            )
            children.append(graph)

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        print("BEFORE RUN SERVER")
        app.layout = html.Div(children=children)
        app.run_server(debug=True)
        print("AFTER RUN SERVER")
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

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        app.layout = html.Div(children=[
            html.H1(children='Hello Dash'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),

            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                }
            )
        ])


class BundleObject():
    """
    A Bundle Object is the classification of BPC data input received by this script.
    """

    DSOBJECT_KEYS = ['Datastore name', 'Capacity', 'Provisioned space', 'Free space', 'Free space percentage']
    VMPROPERTIESOBJ_KEYS = ['Name', 'UUID', 'MemoryMB', 'DS_name', 'DS_capacity', 'DS_freespace']

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

            if str(self.data[0].keys()).__eq__(BundleObject.DSOBJECT_KEYS):
                if len(self.data) == 1:
                    d = DSObject(self.data)
                    return d
                else:
                    d = DSObjectList(self.data)
                    return d

            elif str(self.data[0].keys()) == BundleObject.VMPROPERTIESOBJ_KEYS:
                if len(self.data) == 1:
                    return VMPropObject
                else:
                    return VMPropObjectList

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
