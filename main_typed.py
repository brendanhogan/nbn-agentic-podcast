#!/usr/bin/env python3

"""
Main script for podcast generation pipeline using typed configurations.

This script orchestrates the process of converting a source document into a podcast
using a specified agent configuration.

It performs the following steps:
1. Parses command-line arguments
2. Extracts text from the input document
3. Loads and checks the specified agent configuration
4. Runs the workflow defined in the configuration
5. Outputs the final podcast transcript
"""

import os
import argparse

import utils
import texttospeech


def main():
    parser = argparse.ArgumentParser(description="Generate a podcast from a source document using a specified configuration.")
    parser.add_argument("--input", required=True, help="Path to the input document")
    parser.add_argument("--output", required=True, help="Path to the output folder")
    parser.add_argument("--config", default="IraPod", help="Name of the configuration to use (default: IraPod)")
    parser.add_argument("--llm", default="GPT4O", help="Type of LLM to use (default: GPT4O)")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Initialize LLM
    llm_instance = utils.get_llm_instance(args.llm)

    # Load and check agent configuration
    config_class = utils.get_config_class(args.config)
    config = config_class()

    # Run type checking to make sure workflow is good 
    config.check_workflow()

    # Extract text from input document
    input_processor = utils.get_input_processor(args.input)
    source_text = input_processor.get_text()

    # Run the workflow
    final_transcript = config.run_workflow(llm_instance, args.output, source_text)

    # Save the final transcript
    with open(os.path.join(args.output, "final_transcript.txt"), "w") as f:
        f.write(final_transcript.value)

    # Convert to sound 
    texttospeech.generate_podcast_audio(final_transcript.value,args.output)


    print(f"Podcast generation complete. Output files are in {args.output}")

if __name__ == "__main__":
    main()
