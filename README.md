# NBN-Agentic Podcast

## Description

NBN-Agentic Podcast aims to create a system inspired by notebookLM. It features a modular architecture designed to handle many input types, implements a (light) typed agentic workflow system for secure inter-agent communication, and incorporates a text-to-speech component to produce the final podcast output.

This repository contains the codebase accompanying a detailed blog post, which can be found [here](https://choosealicense.com/licenses/mit/). The blog provides in-depth insights into the project's development and implementation.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
   - [Using main.py](#using-mainpy)
   - [Using main_typed.py](#using-main_typedpy)
3. [Project Structure](#project-structure)
4. [Type System](#type-system)
5. [Agent Configuration](#agent-configuration)
6. [Customization](#customization)
7. [Contributing](#contributing)
8. [License](#license)

## Installation

To set up the NBN-Agentic Podcast project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/nbn-agentic-podcast.git
   cd nbn-agentic-podcast
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

### Using main.py

The `main.py` script provides a standard way to generate a podcast from a source document. To use it:

```python
python main.py --input path/to/your/input/file.pdf --output path/to/output/folder --llm GPT4O
```

Options:
- `--input`: Path to the input document (currently supports PDF)
- `--output`: Path to the output folder where generated files will be saved
- `--llm`: Type of language model to use (default: GPT4O)

### Using main_typed.py

The `main_typed.py` script uses a more advanced configuration system with type checking. To use it:

```python
python main_typed.py --input path/to/your/input/file.pdf --output path/to/output/folder --config IraPod --llm GPT4O
```

Options:
- `--input`: Path to the input document (currently supports PDF)
- `--output`: Path to the output folder where generated files will be saved
- `--config`: Name of the configuration to use (default: IraPod)
- `--llm`: Type of language model to use (default: GPT4O)

## Project Structure

- `agentconfigs.py`: Defines the configuration system for agent workflows
- `agents.py`: Contains the implementation of various agents used in the podcast generation process
- `hosts.py`: Defines classes representing podcast hosts
- `input.py`: Handles input processing and text extraction from different file types
- `infotypes.py`: Defines the typing system for agent inputs and outputs
- `llm.py`: Provides the abstract base class for Language Model interfaces and implementations
- `main.py`: The main script for the standard podcast generation pipeline
- `main_typed.py`: The main script for the typed configuration podcast generation pipeline
- `texttospeech.py`: Handles the conversion of text to speech for the final podcast
- `utils.py`: Contains utility functions used throughout the project

## Type System (`infotypes.py`)
The typing system is defined in `infotypes.py` and consists of several classes that represent different types of information used throughout the podcast generation process. These types serve as a contract between agents, ensuring that the output of one agent can be safely used as input for another.

### Core Types

1. **SourceText**
   - Description: Original source text to be processed
   - Always serves as the initial input to the workflow

2. **Summary**
   - Description: A condensed version of the source text
   - Base class for more specific summary types

3. **Narrative** (subclass of Summary)
   - Description: A focused, story-driven summary of the source text

4. **Acts** (subclass of Summary)
   - Description: A summary divided into distinct narrative acts

5. **IndepthSummary** (subclass of Summary)
   - Description: A detailed, comprehensive summary of the source text

6. **Transcript**
   - Description: A written record of spoken content
   - The final output of the workflow is always a Transcript or its subclass

7. **PersonalizedTranscript** (subclass of Transcript)
   - Description: A transcript tailored to specific preferences or requirements

8. **Bool**
   - Description: A boolean value
   - Used for conditional logic in the workflow

### Type Usage Philosophy

1. **Input Consistency**: `SourceText` is always the initial input to the workflow, ensuring all agents have access to the original content if needed.
2. **Output Consistency**: A `Transcript` (or its subclass) is always the final output, providing a standardized format for the generated podcast content.
3. **Intermediate Types**: Various `Summary` subclasses allow for different levels of content abstraction and focus throughout the workflow.
4. **Type Safety**: By using these defined types, we ensure that agents receive and produce data in expected formats, reducing errors and improving interoperability.

## Agent Configuration

The `agentconfigs.py` file defines the configuration system for agent workflows. The `AgentConfig` abstract base class provides a framework for defining agent workflows. Concrete implementations, like `IraPod`, specify the order of agents and their input/output types.

To create a custom workflow:

1. Subclass `AgentConfig`
2. Implement `get_agents()` to return a dictionary of agent names and their corresponding types
3. Implement `get_workflow()` to define the sequence of steps, inputs, and outputs for each agent

The configuration system supports multi-round or branching processes, allowing for flexible and complex workflows.

The `AgentConfig` class implements a type checker to ensure that the workflow is logically consistent and that the agents' input and output types are compatible. Here's how it works:

1. **Type Checking:**
   - The `type_check_workflow()` method in `AgentConfig` validates the entire workflow:
     - It iterates through each step in the workflow.
     - For each step, it checks if the input types match the output types of the previous steps.
     - It also verifies if the agent's defined input and output types match those specified in the workflow.
   - If any type mismatch is found, a `TypeError` is raised with a detailed error message.

2. **Workflow Execution:**
   - After type checking, the `execute_workflow()` method runs the full workflow:
     - It iterates through the workflow steps defined in the configuration.
     - For each step, it instantiates the corresponding agent.
     - It prepares the input data for the agent based on the outputs from previous steps.
     - It executes the agent's `process()` method with the prepared inputs.
     - The outputs are stored and made available for subsequent steps.


## Customization

To customize the podcast generation process:

1. Create new agent types in `agents.py` by subclassing the `Agent` class
2. Define new input/output types in `infotypes.py` if needed
3. Create a new configuration in `agentconfigs.py` by subclassing `AgentConfig`
4. Modify the `texttospeech.py` file to use different voices or text-to-speech services

## Contributing

Contributions to the NBN-Agentic Podcast project are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

## License

[MIT](https://choosealicense.com/licenses/mit/)

