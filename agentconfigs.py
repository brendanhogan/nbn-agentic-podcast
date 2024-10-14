"""

This module defines the configuration system for agent workflows.

The AgentConfig abstract base class provides a framework for defining
agent workflows. Concrete implementations, like IraPod, specify the
order of agents and their input/output types.

This approach allows for flexible agent configurations while still
enabling type checking between agents. Users can define custom workflows,
including multi-round or branching processes, without being constrained
by a rigid schema.

Type checking can be performed separately to ensure compatibility
between connected agents in the workflow.

"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import agents
import infotypes
import os
import json

class AgentConfig(ABC):
    @abstractmethod
    def get_agents(self) -> Dict[str, type]:
        """
        Returns a dictionary of agent names and their corresponding types.
        
        Returns:
            Dict[str, type]: A dictionary with agent names as keys and their types as values.
        """
        pass

    @abstractmethod
    def get_workflow(self) -> List[Dict[str, Any]]:
        """
        Returns the workflow as a list of steps, each defining inputs and outputs.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a step in the workflow.
            Each step contains:
                - 'agent': The name of the agent for this step
                - 'inputs': A list of input names
                - 'outputs': A list of output names
                - 'condition': Optional. A dictionary with a single element, where the key is either
                               "IF" or "WHILE" and the value is a boolean variable
                - 'iterate': Optional. An integer specifying the number of times to execute this step.
                             Output files will be named with the original output names + "iter_{round}"
        Note:
            - 'source_text' will always be an input name
            - The method should return 'final_transcript' as the final output
        """
        pass

    def check_workflow(self):
        """
        Validates the workflow by checking type compatibility between agents.
        
        Raises:
            TypeError: If there's a type mismatch between agent inputs and outputs.
            ValueError: If there's an invalid workflow configuration.
        """
        agents_dict = self.get_agents()
        workflow = self.get_workflow()

        # Dictionary to keep track of defined inputs
        defined_inputs = {}

        # First input is always source_text
        defined_inputs['source_text'] = infotypes.SourceText
        
        for step in workflow:
            agent_name = step['agent']
            agent_class = agents_dict.get(agent_name)
            if not agent_class:
                raise ValueError(f"Agent '{agent_name}' not found in get_agents()")
            
            agent_instance = agent_class(None)  # Passing None as LLM for type checking
            
            # 1. Check if number of inputs matches expected
            if len(step['inputs']) != len(agent_instance.expected_input_types):
                raise ValueError(f"Number of inputs for agent '{agent_name}' doesn't match expected ({len(step['inputs'])} vs {len(agent_instance.expected_input_types)})")
            # 2 & 3. Check if inputs are newly defined and assign types
            for index, input_name in enumerate(step['inputs']):
                expected_type = agent_instance.expected_input_types[index]
                
                if input_name in defined_inputs:
                    defined_type = defined_inputs[input_name]
                    if not any(issubclass(t, type(defined_type)) and issubclass(t, type(expected_type)) for t in [defined_type.__class__, expected_type.__class__]):
                        raise ValueError(f"Failed to compile workflow: Type mismatch for input '{input_name}' in agent '{agent_name}'")
                else:
                    defined_inputs[input_name] = expected_type

            # 4. Check if number of outputs matches expected
            if len(step['outputs']) != len(agent_instance.output_types):
                raise ValueError(f"Number of outputs for agent '{agent_name}' doesn't match expected ({len(step['outputs'])} vs {len(agent_instance.output_types)})")

            # 5. Check if outputs are not already defined and assign types
            for output_name in step['outputs']:
                if output_name in defined_inputs:
                    raise ValueError(f"Failed to compile workflow: Variable name '{output_name}' is already used as an input in agent '{agent_name}'")
                defined_inputs[output_name] = agent_instance.output_types[step['outputs'].index(output_name)]


            # Check if condition is provided
            if 'condition' in step:
                if len(step['condition']) != 1 or not any(key in step['condition'] for key in ["IF", "WHILE"]):
                    raise ValueError(f"Failed to compile workflow: Condition for agent '{agent_name}' must have a single key 'IF' or 'WHILE'")
                
                condition_key = list(step['condition'].keys())[0]
                condition_var = step['condition'][condition_key]
                
                if condition_var not in defined_inputs:
                    raise ValueError(f"Failed to compile workflow: Condition variable '{condition_var}' for agent '{agent_name}' is not defined")
                
                if defined_inputs[condition_var] != infotypes.Bool:
                    raise ValueError(f"Failed to compile workflow: Condition variable '{condition_var}' for agent '{agent_name}' must be of type Bool")

            # Check if iterate is provided
            if 'iterate' in step:
                if not isinstance(step['iterate'], int):
                    raise ValueError(f"Failed to compile workflow: 'iterate' for agent '{agent_name}' must be an integer")
                
                iterate_count = step['iterate']
                for output_name in step['outputs']:
                    for i in range(iterate_count):
                        iter_output_name = f"{output_name}_iter{i}"
                        if iter_output_name in defined_inputs:
                            raise ValueError(f"Failed to compile workflow: Variable name '{iter_output_name}' is already defined")
                        defined_inputs[iter_output_name] = defined_inputs[output_name]


        # Check if 'final_transcript' exists in defined_inputs and is of type Transcript
        if 'final_transcript' not in defined_inputs:
            raise ValueError("Failed to compile workflow: 'final_transcript' is not defined in the workflow outputs")
        if defined_inputs['final_transcript'] != infotypes.Transcript:
            raise ValueError("Failed to compile workflow: 'final_transcript' must be of type Transcript")
    
        print("Workflow type checked successfully")

    def run_workflow(self, llm, output_dir: str, input_text: str):
        """
        Runs the workflow by calling agents in sequence with the appropriate inputs.

        Args:
            llm: An instance of the LLM class to be used by the agents.
            output_dir (str): The directory where output files will be saved.
            input_text (str): The initial input text for the workflow.

        Returns:
            The final output of the workflow.
        """
        agents_dict = self.get_agents()
        workflow = self.get_workflow()
        
        # Initialize the inputs dictionary with the source text
        inputs = {'source_text': infotypes.SourceText(input_text)}
        
        for step_number, step in enumerate(workflow):
            agent_name = step['agent']
            agent_class = agents_dict[agent_name]
            agent_instance = agent_class(llm)
            
            # Prepare inputs for the agent
            agent_inputs = [inputs[input_name] for input_name in step['inputs']]
            
            # Check if iterate is provided
            if 'iterate' in step:
                iterate_count = step['iterate']
                for iteration in range(iterate_count):
                    # Create a unique filename for this agent's output
                    output_file = os.path.join(output_dir, f"step{step_number}_{agent_name}_iter{iteration}_output.json")
                    # Run the agent
                    outputs = agent_instance.run(agent_inputs, output_file)
                    
                    # Store the outputs with iteration suffix
                    for i, output_name in enumerate(step['outputs']):
                        inputs[f"{output_name}_iter{iteration}"] = outputs[i]
            else:
                # Create a unique filename for this agent's output
                output_file = os.path.join(output_dir, f"step{step_number}_{agent_name}_output.json")
                # Run the agent
                outputs = agent_instance.run(agent_inputs, output_file)
                
                # Store the outputs
                for i, output_name in enumerate(step['outputs']):
                    inputs[output_name] = outputs[i]
        
        # Return the final transcript
        return inputs['final_transcript']

class IraPod(AgentConfig):
    def get_agents(self) -> Dict[str, type]:
        return {
            "NarrativeAgent": agents.NarrativeAgent,
            "ActAgent": agents.ActAgent,
            "ContextualizeAgent": agents.ContextualizeAgent,
            "AnalogyAgent": agents.AnalogyAgent,
            "TranscriptAgent": agents.TranscriptAgent,
            "CombineTranscriptsAgent": agents.CombineTranscriptsAgent,
            "DoubleTranscriptAgent": agents.DoubleTranscriptAgent,
            "PersonalizeAgent": agents.PersonalizeAgent,
        }

    def get_workflow(self) -> List[Dict[str, Any]]:
        return [
            {
                "agent": "NarrativeAgent",
                "inputs": ["source_text"],
                "outputs": ["narrative_output"]
            },
            {
                "agent": "ActAgent",
                "inputs": ["source_text", "narrative_output"],
                "outputs": ["acts_output1", "acts_output2", "acts_output3"]
            },
            {
                "agent": "ContextualizeAgent",
                "inputs": ["source_text", "acts_output1"],
                "outputs": ["contextualized_act1"]
            },
            {
                "agent": "ContextualizeAgent",
                "inputs": ["source_text", "acts_output2"],
                "outputs": ["contextualized_act2"]
            },
            {
                "agent": "ContextualizeAgent",
                "inputs": ["source_text", "acts_output3"],
                "outputs": ["contextualized_act3"]
            },
            {
                "agent": "AnalogyAgent",
                "inputs": ["contextualized_act1"],
                "outputs": ["analogies_act1"]
            },
            {
                "agent": "AnalogyAgent",
                "inputs": ["contextualized_act2"],
                "outputs": ["analogies_act2"]
            },
            {
                "agent": "AnalogyAgent",
                "inputs": ["contextualized_act3"],
                "outputs": ["analogies_act3"]
            },
             {
                "agent": "TranscriptAgent",
                "inputs": ["acts_output1", "analogies_act1", "acts_output2", "analogies_act2", "acts_output3", "analogies_act3"],
                "outputs": ["transcript_draft"], 
                "iterate": 3,
            },           
            {
                "agent": "CombineTranscriptsAgent",
                "inputs": ["transcript_draft_iter0","transcript_draft_iter1","transcript_draft_iter2"],
                "outputs": ["combined_transcript"]
            },
            {
                "agent": "DoubleTranscriptAgent",
                "inputs": ["combined_transcript"],
                "outputs": ["double_transcript"]
            },
            {
                "agent": "PersonalizeAgent",
                "inputs": ["double_transcript"],
                "outputs": ["final_transcript"]
            },
        ]
    

if __name__ == "__main__":
    config = IraPod()
    config.check_workflow()





    #
