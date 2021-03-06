from __future__ import print_function
import os
import networkx as nx
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# from networkx.readwrite.json_graph import node_link_data

# -----------------------------------------------------------------------------


class SystemTopology(object):

    orientation = "LR"          # Orientation of graph - Graphviz option
    connector_type = "spline"   # Connector appearance - Graphviz option
    clustering = False          # Cluster based on defined `node_cluster`

    out_file = "system_topology"
    graph_label = "System Component Topology"

    def __init__(self, infrastructure, scenario):

        self.infrastructure = infrastructure
        self.scenario = scenario
        self.gviz = ""  # placeholder for a pygraphviz agraph
        self.component_attr = {}  # Dict for system comp attributes
        self.out_dir = ""

        for comp_id in infrastructure.components.keys():
            self.component_attr[comp_id] = \
                vars(infrastructure.components[comp_id])

        self.graph_label = "System Component Topology"
        self.out_dir = scenario.output_path

        if infrastructure.system_class.lower() in \
                ['potablewatertreatmentplant', 'pwtp',
                 'wastewatertreatmentplant', 'wwtp',
                 'substation']:
            self.orientation = "TB"
            self.connector_type = "ortho"
            self.clustering = True
        elif infrastructure.system_class.lower() in \
                ['powerstation']:
            self.orientation = "LR"
            self.connector_type = "ortho"
            self.clustering = True
        else:
            self.orientation = "TB"
            self.connector_type = "polyline"
            self.clustering = False

        # Default drawing program
        self.drawing_prog = 'dot'

        # Overwrite default if node locations are defined
        if hasattr(infrastructure, 'system_meta'):
            if infrastructure.system_meta['component_location_conf']['value']\
                    == 'defined':
                self.drawing_prog = 'neato'


    def draw_sys_topology(self, viewcontext):

        if self.infrastructure.system_class.lower() in ['substation']:
            self.draw_substation_topology(viewcontext)
        elif self.infrastructure.system_class.lower() in [
            "potablewatertreatmentplant", "pwtp",
            "wastewatertreatmentplant", "wwtp",
            "watertreatmentplant", "wtp"]:
            self.draw_wtp_topology(viewcontext)
        else:
            self.draw_generic_sys_topology(viewcontext)


    def draw_generic_sys_topology(self, viewcontext):
        """
        Draws the component configuration for a given infrastructure system.

        :param viewcontext: Option "as-built" indicates topology of system
        prior to hazard impact. Other options can be added to reflect
        post-impact system configuration and alternate designs.
        :return: generates and saves the system topology diagram in the
        following formats: (graphviz) dot, png, svg.
        """

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Set up output file names & location

        if not self.out_dir.strip():
            output_path = os.getcwd()
        else:
            output_path = self.out_dir

        # strip away file ext and add our own
        fname = self.out_file.split(os.extsep)[0]

        # Orientation of the graph (default is top-to-bottom):
        if self.orientation.upper() not in ['TB', 'LR', 'RL', 'BT']:
            self.orientation = 'TB'

        # `connector_type` refers to the line connector type. Must be one of
        # the types supported by Graphviz (i.e. 'spline', 'ortho', 'line',
        # 'polyline', 'curved')
        if self.connector_type.lower() not in \
                ['spline', 'ortho', 'line', 'polyline', 'curved']:
            self.connector_type = 'ortho'

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Draw graph using pygraphviz. Define general node & edge attributes.

        G = self.infrastructure._component_graph.digraph
        graphml_file = os.path.join(output_path, fname + '.graphml')
        G.write_graphml(graphml_file)

        elist = G.get_edgelist()
        named_elist = []
        for tpl in elist:
            named_elist.append((G.vs[tpl[0]]['name'],
                                G.vs[tpl[1]]['name']))
        nxG = nx.DiGraph(named_elist)

        self.gviz = nx.nx_agraph.to_agraph(nxG)

        default_node_color = "royalblue3"
        default_edge_color = "royalblue2"

        self.gviz.graph_attr.update(
            concentrate=False,
            resolution=300,
            directed=True,
            labelloc="t",
            label='< '+self.graph_label+'<BR/><BR/> >',
            rankdir=self.orientation,
            #ranksep="1.0 equally",
            splines=self.connector_type,
            center="true",
            forcelabels=True,
            fontname="Helvetica-Bold",
            fontcolor="#444444",
            fontsize=26,
            smoothing="graph_dist",
            pad=0.5,
            nodesep=1.5,
            sep=1.0,
            overlap="voronoi",
            overlap_scaling=1.0,
            )

        self.gviz.node_attr.update(
            shape="circle",
            style="rounded,filled",
            fixedsize="true",
            width=1.8,
            height=1.8,
            xlp="0, 0",
            color=default_node_color,  # gray14
            fillcolor="white",
            fontcolor=default_node_color,  # gray14
            penwidth=1.5,
            fontname="Helvetica-Bold",
            fontsize=18,
            )

        self.gviz.edge_attr.update(
            arrowhead="normal",
            arrowsize="1.0",
            style="bold",
            color=default_edge_color,  # gray12
            penwidth=1.2,
            )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Customise nodes based on node type or defined clusters

        for node in self.component_attr.keys():
            label_mod = self.segment_long_labels(node, delims=['_', ' '])
            self.gviz.get_node(node).attr['label'] = label_mod

            if str(self.component_attr[node]['node_type']).lower() == 'supply':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=12, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="rect",
                    rank="supply",
                    style="rounded,filled",
                    fixedsize="true",
                    color="limegreen",
                    fillcolor="white",
                    fontcolor="limegreen",
                    penwidth=2.0,
                    height=1.2,
                    width=2.2,
                    )

            if str(self.component_attr[node]['node_type']).lower() == 'sink':
                self.gviz.get_node(node).attr.update(
                    shape="doublecircle",
                    rank="sink",
                    penwidth=2.0,
                    color="orangered",  # royalblue3
                    fillcolor="white",
                    fontcolor="orangered",  # royalblue3
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'dependency':
                self.gviz.get_node(node).attr.update(
                    shape="circle",
                    rank="dependency",
                    penwidth=3.5,
                    color="orchid",
                    fillcolor="white",
                    fontcolor="orchid"
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'junction':
                self.gviz.get_node(node).attr.update(
                    shape="point",
                    width=0.5,
                    height=0.5,
                    penwidth=3.5,
                    color=default_node_color,
                    )

        # Clustering: whether to create subgraphs based on `node_cluster`
        #             designated for components
        node_clusters = list(set([self.component_attr[k]['node_cluster']
                                  for k in self.component_attr.keys()]))
        if self.clustering:
            for cluster in node_clusters:
                grp = [k for k in self.component_attr.keys()
                       if self.component_attr[k]['node_cluster'] == cluster]
                cluster = '_'.join(cluster.split())
                if cluster.lower() not in ['none', '']:
                    cluster_name = 'cluster_'+cluster
                    rank = 'same'
                else:
                    cluster_name = ''
                    rank = ''
                self.gviz.add_subgraph(
                    nbunch=grp,
                    name=cluster_name,
                    style='invis',
                    label='',
                    clusterrank='local',
                    rank=rank,
                    )

        for node in self.component_attr.keys():
            pos_x = self.component_attr[node]['longitude']
            pos_y = self.component_attr[node]['latitude']
            if pos_x and pos_y:
                node_pos = str(pos_x)+","+str(pos_y)+"!"
                self.gviz.get_node(node).attr.update(pos=node_pos)

        # self.gviz.layout(prog=self.drawing_prog)
        if viewcontext == "as-built":
            self.gviz.write(os.path.join(output_path, fname + '_gv.dot'))
            self.gviz.draw(os.path.join(output_path, fname + '_dot.png'),
                           format='png', prog='dot',
                           args='-Gdpi=300')
            self.gviz.draw(os.path.join(output_path, fname + '.png'),
                           format='png', prog=self.drawing_prog,
                           args='-n2')

        self.gviz.draw(os.path.join(output_path, fname + '.svg'),
                       format='svg',
                       prog=self.drawing_prog)


        # nx.readwrite.json_graph.node_link_data(self.gviz,
        #                   os.path.join(output_path, fname + '.json'))

    # ==========================================================================

    def draw_substation_topology(self, viewcontext):
        """
        Draws the component configuration for a substation.

        :param viewcontext: Option "as-built" indicates topology of system
        prior to hazard impact. Other options can be added to reflect
        post-impact system configuration and alternate designs.
        :return: generates and saves the system topology diagram in the
        following formats: (graphviz) dot, png, svg.
        """

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Set up output file names & location

        if not self.out_dir.strip():
            output_path = os.getcwd()
        else:
            output_path = self.out_dir

        # strip away file ext and add our own
        fname = self.out_file.split(os.extsep)[0]

        # Orientation of the graph (default is top-to-bottom):
        self.orientation = 'TB'

        # `connector_type` refers to the line connector type. Must be one of
        # ['spline', 'ortho', 'line', 'polyline', 'curved']
        self.connector_type = 'ortho'
        self.drawing_prog = 'neato'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        G = self.infrastructure._component_graph.digraph
        graphml_file = os.path.join(output_path, fname + '.graphml')
        G.write_graphml(graphml_file)

        elist = G.get_edgelist()
        named_elist = []
        for tpl in elist:
            named_elist.append((G.vs[tpl[0]]['name'],
                                G.vs[tpl[1]]['name']))
        nxG = nx.DiGraph(named_elist)

        self.gviz = nx.nx_agraph.to_agraph(nxG)

        default_node_color = "royalblue3"
        default_edge_color = "royalblue2"

        self.gviz.graph_attr.update(
            directed=True,
            concentrate=False,
            resolution=300,
            orientation="portrait",
            labelloc="t",
            label='< '+self.graph_label+'<BR/><BR/> >',
            bgcolor="white",
            rankdir=self.orientation,
            # ranksep="1.0 equally",
            splines=self.connector_type,
            center="true",
            forcelabels=True,
            fontname="Helvetica-Bold",
            fontcolor="#444444",
            fontsize=26,
            # smoothing="graph_dist",
            smoothing="none",
            pad=0.5,
            pack=False,
            sep="+20",
            # overlap=False,
            # overlap="voronoi",
            # overlap_scaling=1.0,
            )

        self.gviz.node_attr.update(
            shape="circle",
            style="rounded,filled",
            fixedsize="true",
            width=0.2,
            height=0.2,
            color=default_node_color,  # gray14
            fillcolor="white",
            fontcolor=default_node_color,  # gray14
            penwidth=1.5,
            fontname="Helvetica-Bold",
            fontsize=12,
            )

        self.gviz.edge_attr.update(
            arrowhead="normal",
            arrowsize="0.7",
            style="bold",
            color=default_edge_color,  # gray12
            penwidth=1.0,
            )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clustering: whether to create subgraphs based on `node_cluster`
        #             designated for components
        node_clusters = list(set([self.component_attr[k]['node_cluster']
                                  for k in self.component_attr.keys()]))
        if self.clustering:
            for cluster in node_clusters:
                grp = [k for k in self.component_attr.keys()
                       if self.component_attr[k]['node_cluster'] == cluster]
                cluster = '_'.join(cluster.split())
                if cluster.lower() not in ['none', '']:
                    cluster_name = 'cluster_'+cluster
                    rank = 'same'
                else:
                    cluster_name = ''
                    rank = ''
                self.gviz.add_subgraph(
                    nbunch=grp,
                    name=cluster_name,
                    style='invis',
                    label='',
                    clusterrank='local',
                    rank=rank,
                    )

        for node in self.component_attr.keys():
            pos_x = self.component_attr[node]['longitude']
            pos_y = self.component_attr[node]['latitude']
            if pos_x and pos_y:
                node_pos = str(pos_x)+","+str(pos_y)+"!"
                self.gviz.get_node(node).attr.update(pos=node_pos)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Customise nodes based on node type or defined clusters

        for node in self.component_attr.keys():
            # label_mod = self.segment_long_labels(node, delims=['_', ' '])
            # self.gviz.get_node(node).attr['label'] = label_mod

            if str(self.component_attr[node]['node_type']).lower() == 'supply':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=10, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="rect",
                    rank="supply",
                    style="filled",
                    fixedsize="true",
                    color="limegreen",
                    fillcolor="white",
                    fontcolor="limegreen",
                    peripheries=2,
                    penwidth=1.5,
                    height=0.8,
                    width=1.5,
                    )

            if str(self.component_attr[node]['node_type']).lower() == 'sink':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=7, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="doublecircle",
                    width=0.9,
                    height=0.9,
                    rank="sink",
                    penwidth=1.5,
                    color="orangered",  # royalblue3
                    fillcolor="white",
                    fontcolor="orangered",  # royalblue3
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'dependency':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=7, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="circle",
                    width=0.9,
                    height=0.9,
                    rank="dependency",
                    penwidth=2.5,
                    color="orchid",
                    fillcolor="white",
                    fontcolor="orchid"
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'junction':
                self.gviz.get_node(node).attr.update(
                    shape="point",
                    width=0.2,
                    height=0.2,
                    color="#777777",
                    fillcolor="#777777",
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'transshipment':
                self.gviz.get_node(node).attr.update(
                    fixedsize="true",
                    label="",
                    xlabel=node,
                    # shape="circle",
                    # style="rounded,filled",
                    # width=0.2,
                    # height=0.2,
                    # penwidth=1.5,
                    # color=default_node_color,
                    )

            if str(self.component_attr[node]['component_class']).lower()\
                    == 'bus':
                # POSITION MUST BE IN POINTS for this to work
                # tpos = self.gviz.get_node(node).attr['pos']
                # poslist = [int(x.strip("!")) for x in tpos.split(",")]
                # posnew = str(poslist[0]) + "," + str(poslist[1] + 5) + "!"
                self.gviz.get_node(node).attr.update(
                    shape="rect",
                    penwidth=1.0,
                    width=1.0,
                    height=0.2,
                    label="",
                    xlabel=node,
                    # xlp=posnew,
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Draw the graph

        if viewcontext == "as-built":
            self.gviz.write(os.path.join(output_path, fname + '_gv.dot'))
            self.gviz.draw(os.path.join(output_path, fname + '_dot.png'),
                           format='png', prog='dot',
                           args='-Gdpi=300 -Gsize=8.27,11.69\!')

            self.gviz.draw(os.path.join(output_path, fname + '.png'),
                           format='png', prog=self.drawing_prog,
                           args='-n -Gdpi=300')

        self.gviz.draw(os.path.join(output_path, fname + '.svg'),
                       format='svg',
                       prog=self.drawing_prog)

    # ==========================================================================
    def draw_wtp_topology(self, viewcontext):
        """
        Draws the component configuration for a water treatment plant.

        :param viewcontext: Option "as-built" indicates topology of system
        prior to hazard impact. Other options can be added to reflect
        post-impact system configuration and alternate designs.
        :return: generates and saves the system topology diagram in the
        following formats: (graphviz) dot, png, svg.
        """

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Set up output file names & location

        if not self.out_dir.strip():
            output_path = os.getcwd()
        else:
            output_path = self.out_dir

        # strip away file ext and add our own
        fname = self.out_file.split(os.extsep)[0]

        # Orientation of the graph (default is top-to-bottom):
        self.orientation = 'TB'

        # `connector_type` refers to the line connector type. Must be one of
        # ['spline', 'ortho', 'line', 'polyline', 'curved']
        self.connector_type = 'ortho'
        self.drawing_prog = 'neato'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        G = self.infrastructure._component_graph.digraph
        graphml_file = os.path.join(output_path, fname + '.graphml')
        G.write_graphml(graphml_file)

        elist = G.get_edgelist()
        named_elist = []
        for tpl in elist:
            named_elist.append((G.vs[tpl[0]]['name'],
                                G.vs[tpl[1]]['name']))
        nxG = nx.DiGraph(named_elist)

        self.gviz = nx.nx_agraph.to_agraph(nxG)

        default_node_color = "royalblue3"
        default_edge_color = "royalblue2"

        self.gviz.graph_attr.update(
            directed=True,
            concentrate=False,
            resolution=300,
            orientation="portrait",
            labelloc="t",
            label='< '+self.graph_label+'<BR/><BR/> >',
            bgcolor="white",
            rankdir=self.orientation,
            # ranksep="1.0 equally",
            splines=self.connector_type,
            center="true",
            forcelabels=True,
            fontname="Helvetica-Bold",
            fontcolor="#444444",
            fontsize=26,
            # smoothing="graph_dist",
            smoothing="none",
            pad=0.5,
            pack=False,
            sep="+20",
            )

        self.gviz.node_attr.update(
            shape="circle",
            style="filled",
            fixedsize="true",
            width=0.3,
            height=0.3,
            color=default_node_color,  # gray14
            fillcolor="white",
            fontcolor=default_node_color,  # gray14
            penwidth=1.5,
            fontname="Helvetica-Bold",
            fontsize=12,
            )

        self.gviz.edge_attr.update(
            arrowhead="normal",
            arrowsize="0.7",
            style="bold",
            color=default_edge_color,  # gray12
            penwidth=1.0,
            )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clustering: whether to create subgraphs based on `node_cluster`
        #             designated for components
        node_clusters = list(set([self.component_attr[k]['node_cluster']
                                  for k in self.component_attr.keys()]))
        if self.clustering:
            for cluster in node_clusters:
                grp = [k for k in self.component_attr.keys()
                       if self.component_attr[k]['node_cluster'] == cluster]
                cluster = '_'.join(cluster.split())
                if cluster.lower() not in ['none', '']:
                    cluster_name = 'cluster_'+cluster
                    rank = 'same'
                else:
                    cluster_name = ''
                    rank = ''
                self.gviz.add_subgraph(
                    nbunch=grp,
                    name=cluster_name,
                    style='invis',
                    label='',
                    clusterrank='local',
                    rank=rank,
                    )

        for node in self.component_attr.keys():
            pos_x = self.component_attr[node]['longitude']
            pos_y = self.component_attr[node]['latitude']
            if pos_x and pos_y:
                node_pos = str(pos_x)+","+str(pos_y)+"!"
                self.gviz.get_node(node).attr.update(pos=node_pos)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Customise nodes based on node type or defined clusters

        for node in self.component_attr.keys():
            # label_mod = self.segment_long_labels(node, delims=['_', ' '])
            # self.gviz.get_node(node).attr['label'] = label_mod

            if str(self.component_attr[node]['node_type']).lower() == 'supply':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=10, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="ellipse",
                    rank="supply",
                    fixedsize="true",
                    color="limegreen",
                    fillcolor="white",
                    fontcolor="limegreen",
                    penwidth=1.5,
                    width=1.5,
                    height=0.9,
                    )

            if str(self.component_attr[node]['node_type']).lower() == 'sink':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=7, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="ellipse",
                    rank="sink",
                    color="orangered",  # royalblue3
                    fillcolor="white",
                    fontcolor="orangered",  # royalblue3
                    peripheries=2,
                    penwidth=1.5,
                    width=1.5,
                    height=0.9,
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'dependency':
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=7, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="circle",
                    width=1.0,
                    height=1.0,
                    rank="dependency",
                    penwidth=2.5,
                    color="orchid",
                    fillcolor="white",
                    fontcolor="orchid"
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'junction':
                tmplabel =\
                    self.segment_long_labels(node, maxlen=8, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="point",
                    width=0.3,
                    height=0.3,
                    color="#888888",
                    fillcolor="#888888",
                    fontcolor="#888888",
                    label="",
                    xlabel=tmplabel,
                    )

            if str(self.component_attr[node]['node_type']).lower() \
                    == 'transshipment':
                self.gviz.get_node(node).attr.update(
                    width=0.3,
                    height=0.3,
                    fixedsize="true",
                    label="",
                    xlabel=node,
                    )

            if str(self.component_attr[node]['component_class']).lower() in \
                    ['large tank',
                     'sedimentation basin',
                     'sedimentation basin - large']:
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=15, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="rect",
                    penwidth=1.0,
                    width=2.5,
                    height=0.9,
                    xlabel="",
                    )

            if str(self.component_attr[node]['component_class']).lower() in\
                    ['small tank',
                     'sedimentation basin - small',
                     'chlorination tank']:
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=12, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="rect",
                    penwidth=1.0,
                    width=1.5,
                    height=0.9,
                    xlabel="",
                    )

            if str(self.component_attr[node]['component_class']).lower()\
                    == 'chemical tank':
                self.gviz.get_node(node).attr.update(
                    # shape="cylinder",
                    shape="circle",
                    penwidth=1.0,
                    width=0.7,
                    height=0.7,
                    fixedsize="true",
                    label="",
                    xlabel=node,
                    )

            if str(self.component_attr[node]['component_class']).lower() in\
                ['building', 'small building']:
                tmplabel =\
                    self.segment_long_labels(node, maxlen=12, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="house",
                    penwidth=2.0,
                    width=1.6,
                    height=0.9,
                    label=tmplabel,
                    xlabel="",
                    )

            if str(self.component_attr[node]['component_class']).lower() in\
                    ['pump', 'pumps']:
                tmplabel =\
                    self.segment_long_labels(node, maxlen=12, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="hexagon",
                    penwidth=1.0,
                    width=0.5,
                    height=0.5,
                    fixedsize="true",
                    label="",
                    xlabel=tmplabel,
                    )

            if str(self.component_attr[node]['component_class']).lower() in \
                    ['switchroom', 'power supply']:
                self.gviz.get_node(node).attr['label'] =\
                    self.segment_long_labels(node, maxlen=15, delims=['_', ' '])
                self.gviz.get_node(node).attr.update(
                    shape="rect",
                    style="rounded",
                    penwidth=1.0,
                    width=1.6,
                    height=0.9,
                    xlabel="",
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Draw the graph

        if viewcontext == "as-built":
            self.gviz.draw(os.path.join(output_path, fname + '.png'),
                           format='png', prog=self.drawing_prog,
                           args='-n -Gdpi=300')
            self.gviz.draw(os.path.join(output_path, fname + '.jpg'),
                           format='jpg', prog=self.drawing_prog,
                           args='-n -Gdpi=300')
            self.gviz.write(os.path.join(output_path, fname + '_gv.dot'))
            self.gviz.draw(os.path.join(output_path, fname + '_dot.png'),
                           format='png', prog='dot',
                           args='-Gdpi=300 -Gsize=8.27,11.69\!')

        self.gviz.draw(os.path.join(output_path, fname + '.svg'),
                       format='svg',
                       prog=self.drawing_prog)

    # ==========================================================================

    def msplit(self, string, delims):
        s = string
        for d in delims:
            rep = d + '\n'
            s = rep.join(x for x in s.split(d))
        return s

    def segment_long_labels(self, string, maxlen=7, delims=' '):
        if (not delims) and (len(string) > maxlen):
            return "\n".join(
                re.findall("(?s).{," + str(maxlen) + "}", string))[:-1]
        elif len(string) > maxlen:
            return self.msplit(string, delims)
        else:
            return string

