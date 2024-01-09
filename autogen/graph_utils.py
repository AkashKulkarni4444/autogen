from typing import List, Dict
import logging

from autogen.agentchat.groupchat import GroupChat, Agent, ConversableAgent

def check_graph_validity(allowed_graph_dict: dict, agents: List[Agent], allow_repeat_speaker: bool = False):
        """
        allowed_graph_dict: A dictionary of keys and list as values. The keys are the names of the agents, and the values are the names of the agents that the key agent can transition to.
        agents: A list of Agents
        allow_repeat_speaker: A boolean indicating whether the same agent can speak twice in a row.

        Checks for the following:
            Errors
            1. The dictionary must have a structure of keys and list as values
            2. Every key exists in agents' names.
            3. Every value is a list of Agents (not string).
            4. The graph has at least one node
            5. The graph has at least one edge
            6. If self.allow_repeat_speaker is False, then the graph has no self-loops

            Warnings
            1. Warning if there are isolated agent nodes
            2. Warning if there are any agents in self.agents not in graph
        """

        ### Errors

        # Check 1. The dictionary must have a structure of keys and list as values
        if not isinstance(allowed_graph_dict, dict):
            raise ValueError("The graph must be a dictionary.")
        
        # All values must be lists of Agent or empty
        if not all([isinstance(value, list) or value == [] for value in allowed_graph_dict.values()]):
            raise ValueError("The graph must be a dictionary of keys and list as values.")
                
        # Check 2. Every key exists in agents
        if not all([key in [agent.name for agent in agents] for key in allowed_graph_dict.keys()]):
            raise ValueError("The graph has keys not in agents' names.")
        
        # Check 3. Every value is a list of Agents or empty list (not string).
        if not all([all([isinstance(agent, Agent) for agent in value]) for value in allowed_graph_dict.values()]):
            raise ValueError("The graph has values that are not lists of Agents.")
        
        # Check 4. The graph has at least one node
        if len(allowed_graph_dict.keys()) == 0:
            raise ValueError("The graph has no nodes.")
        
        # Check 5. The graph has at least one edge
        if len(sum(allowed_graph_dict.values(), [])) == 0:
            raise ValueError("The graph has no edges.")
        
        # Check 6. If self.allow_repeat_speaker is False, then the graph has no self-loops
        if not allow_repeat_speaker:
            if any([key in value for key, value in allowed_graph_dict.items()]):
                raise ValueError("The graph has self-loops.")
            
        # Warnings
        # Warning 1. Warning if there are isolated agent nodes
        if any([len(value) == 0 for value in allowed_graph_dict.values()]):
            logging.warning("Warning: There are isolated agent nodes.")

        # Warning 2. Warning if there are any agents in self.agents not in graph
        if any([agent.name not in allowed_graph_dict.keys() for agent in agents]):
            logging.warning("Warning: There are agents in self.agents not in graph.")

def invert_disallowed_to_allowed(disallowed_graph_dict: dict, agents: List[Agent]) -> dict:
    """
    Start with a fully connected graph of all agents. Remove edges from the fully connected graph according to the disallowed_graph_dict to form the allowed_graph_dict.
    """

    # Create a fully connected graph
    allowed_graph_dict = {agent.name: [other_agent for other_agent in agents if other_agent != agent] for agent in agents}

    # Remove edges from the fully connected graph according to the disallowed_graph_dict
    for key, value in disallowed_graph_dict.items():
        allowed_graph_dict[key] = [agent for agent in allowed_graph_dict[key] if agent not in value]

    return allowed_graph_dict
    