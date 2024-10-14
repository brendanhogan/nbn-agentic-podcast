#!/usr/bin/env python3

"""
Main script for podcast generation pipeline using a hardcoded workflow.

This script orchestrates the process of converting a source document into a podcast
using a predefined sequence of agents.

It performs the following steps:
1. Parses command-line arguments
2. Extracts text from the input document
3. Initializes and runs each agent in the workflow sequence
4. Outputs the final podcast transcript
"""

import os
import argparse
import utils
import texttospeech
import agents
import infotypes

def run_workflow(llm, output_dir: str, input_text: str):
    """
    Runs the hardcoded workflow by calling agents in sequence with the appropriate inputs.

    Args:
        llm: An instance of the LLM class to be used by the agents.
        output_dir (str): The directory where output files will be saved.
        input_text (str): The initial input text for the workflow.

    Returns:
        The final output of the workflow.
    """
    inputs = {'source_text': infotypes.SourceText(input_text)}
    
    # Step 1: NarrativeAgent
    narrative_agent = agents.NarrativeAgent(llm)
    narrative_output = narrative_agent.run([inputs['source_text']], os.path.join(output_dir, "step1_NarrativeAgent_output.json"))[0]
    inputs['narrative_output'] = narrative_output

    # Step 2: ActAgent
    act_agent = agents.ActAgent(llm)
    acts_outputs = act_agent.run([inputs['source_text'], inputs['narrative_output']], os.path.join(output_dir, "step2_ActAgent_output.json"))
    inputs['acts_output1'], inputs['acts_output2'], inputs['acts_output3'] = acts_outputs

    # Steps 3-5: ContextualizeAgent
    contextualize_agent = agents.ContextualizeAgent(llm)
    for i in range(1, 4):
        contextualized_act = contextualize_agent.run([inputs['source_text'], inputs[f'acts_output{i}']], os.path.join(output_dir, f"step{i+2}_ContextualizeAgent_output.json"))[0]
        inputs[f'contextualized_act{i}'] = contextualized_act

    # Steps 6-8: AnalogyAgent
    analogy_agent = agents.AnalogyAgent(llm)
    for i in range(1, 4):
        analogies_act = analogy_agent.run([inputs[f'contextualized_act{i}']], os.path.join(output_dir, f"step{i+5}_AnalogyAgent_output.json"))[0]
        inputs[f'analogies_act{i}'] = analogies_act

    # Step 9: TranscriptAgent (iterate 3 times)
    transcript_agent = agents.TranscriptAgent(llm)
    for i in range(3):
        transcript_inputs = [inputs[f'acts_output{j}'] for j in range(1, 4)] + [inputs[f'analogies_act{j}'] for j in range(1, 4)]
        transcript_draft = transcript_agent.run(transcript_inputs, os.path.join(output_dir, f"step9_TranscriptAgent_iter{i}_output.json"))[0]
        inputs[f'transcript_draft_iter{i}'] = transcript_draft

    # Step 10: CombineTranscriptsAgent
    combine_transcripts_agent = agents.CombineTranscriptsAgent(llm)
    combined_transcript = combine_transcripts_agent.run([inputs[f'transcript_draft_iter{i}'] for i in range(3)], os.path.join(output_dir, "step10_CombineTranscriptsAgent_output.json"))[0]
    inputs['combined_transcript'] = combined_transcript

    # Step 11: DoubleTranscriptAgent
    double_transcript_agent = agents.DoubleTranscriptAgent(llm)
    double_transcript = double_transcript_agent.run([inputs['combined_transcript']], os.path.join(output_dir, "step11_DoubleTranscriptAgent_output.json"))[0]
    inputs['double_transcript'] = double_transcript

    # Step 12: PersonalizeAgent
    personalize_agent = agents.PersonalizeAgent(llm)
    final_transcript = personalize_agent.run([inputs['double_transcript']], os.path.join(output_dir, "step12_PersonalizeAgent_output.json"))[0]
    
    return final_transcript

def main():
    parser = argparse.ArgumentParser(description="Generate a podcast from a source document using a hardcoded workflow.")
    parser.add_argument("--input", required=True, help="Path to the input document")
    parser.add_argument("--output", required=True, help="Path to the output folder")
    parser.add_argument("--llm", default="GPT4O", help="Type of LLM to use (default: GPT4O)")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Initialize LLM
    llm_instance = utils.get_llm_instance(args.llm)

    # Extract text from input document
    input_processor = utils.get_input_processor(args.input)
    source_text = input_processor.get_text()

    # Run the workflow
    final_transcript = run_workflow(llm_instance, args.output, source_text)

    # Save the final transcript
    with open(os.path.join(args.output, "final_transcript.txt"), "w") as f:
        f.write(final_transcript.value)

    # Convert to sound 
    texttospeech.generate_podcast_audio(final_transcript.value, args.output)

    print(f"Podcast generation complete. Output files are in {args.output}")

if __name__ == "__main__":
    main()
