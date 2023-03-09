from typing import Dict, List

import networkx as nx
from parchmint import Target
from pymint.mintdevice import MINTDevice

from lfr.netlistgenerator.connectingoption import ConnectingOption
from lfr.netlistgenerator.constructiongraph.constructiongraph import ConstructionGraph
from lfr.netlistgenerator.mappinglibrary import MappingLibrary
from lfr.netlistgenerator.namegenerator import NameGenerator
from lfr.netlistgenerator.primitive import PrimitiveType


def generate_device(
    construction_graph: ConstructionGraph,
    scaffhold_device: MINTDevice,
    name_generator: NameGenerator,
    mapping_library: MappingLibrary,
) -> None:
    # TODO - Generate the device
    # Step 1 - go though each of the construction nodes and genrate the corresponding
    # components
    # Step 2 - generate the connections between the outputs to input on the connected
    # construction nodes
    # Step 3 - TODO - Generate the control network

    cn_component_mapping: Dict[str, List[str]] = {}

    node_ids = nx.dfs_preorder_nodes(construction_graph)
    print("Nodes to Traverse:", node_ids)

    # Go through the ordered nodes and start creating the components
    for node_id in node_ids:
        cn = construction_graph.get_construction_node(node_id)

        # raise and error if the construction node has no primitive
        if cn.primitive is None:
            raise Exception("Construction Node has no primitive")

        # Generate the netlist based on the primitive type
        if cn.primitive.type is PrimitiveType.COMPONENT:
            # Generate the component
            component = cn.primitive.get_default_component(
                name_generator, scaffhold_device.device.layers[0]
            )

            # Add to the scaffhold device
            scaffhold_device.device.add_component(component)

            # Add to the component mapping
            cn_component_mapping[node_id] = [component.ID]

        elif cn.primitive.type is PrimitiveType.NETLIST:
            netlist = cn.primitive.get_default_netlist(cn.ID, name_generator)

            # Merge the netlist into the scaffhold device
            scaffhold_device.device.merge_netlist(netlist)

            # Add to the component mapping
            cn_component_mapping[node_id] = [
                component.ID for component in netlist.components
            ]

    # Go through the edges and connect the components using the inputs and outputs of
    # the primitives
    for source_cn_id, target_cn_id in construction_graph.edges:
        source_cn = construction_graph.get_construction_node(source_cn_id)
        target_cn = construction_graph.get_construction_node(target_cn_id)

        # Get the output ConnectingOptions of the source cn
        output_options = source_cn.output_options
        input_options = target_cn.input_options

        # Pop and make a connection between the output and the input
        source_option = output_options.pop()
        target_option = input_options.pop()

        # Generate the target from the source option
        source_targets = get_targets(
            source_option, source_cn_id, name_generator, cn_component_mapping
        )
        target_targets = get_targets(
            target_option, target_cn_id, name_generator, cn_component_mapping
        )

        # If there is 1 source and 1 target, then connect the components
        if len(source_targets) == 1 and len(target_targets) == 1:
            create_device_connection(
                source_targets.pop(),
                target_targets.pop(),
                name_generator,
                scaffhold_device,
                mapping_library,
            )

        elif len(source_targets) == len(target_targets):
            raise NotImplementedError("Bus targets not implemented")
        elif len(source_targets) == 1 and len(target_targets) > 1:
            raise NotImplementedError("Multiple targets not implemented")
        elif len(source_targets) > 1 and len(target_targets) == 1:
            raise NotImplementedError("Multiple sources not implemented")


def create_device_connection(
    source_target: Target,
    target_target: Target,
    name_generator: NameGenerator,
    scaffhold_device: MINTDevice,
    mapping_library: MappingLibrary,
) -> None:
    # TODO - Create the connection based on parameters from the connecting option
    raise NotImplementedError("Not implemented")


def get_targets(
    option: ConnectingOption,
    connection_node_id: str,
    name_generator: NameGenerator,
    cn_name_map,
) -> List[Target]:
    ret: List[Target] = []

    component_name: str = ""
    if option.component_name is None:
        # This is the case where the mapping option is for component primitive
        component_name = cn_name_map[connection_node_id]
    else:
        # This is the case where the mapping option is for netlist primitive
        old_name = option.component_name
        component_name = name_generator.get_name(old_name)

    for port_name in option.component_port:
        # Check and make sure that the component name is valid
        if component_name is None:
            raise Exception(
                "Could not generate connection target since Port name is None"
            )
        target = Target(component_name, port_name)
        ret.append(target)

    return ret