"""
Holds agent abstract class, as well as all agents used for podcast transcript generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union

import os
import json


import llm
import hosts
import infotypes

class Agent(ABC):
    """
    Abstract base class for all agents used in podcast transcript generation.
    """

    def __init__(self, llm_call: llm.LLM, name: str):
        """
        Initialize the agent with a language model call and a name.

        Args:
            llm_call (llm.LLM): An instance of a language model call.
            name (str): The name of the agent.
        """
        self.llm_call = llm_call
        self.name = name
        self.expected_input_types = []
        self.output_types = []

    def get_description(self) -> Dict[str, Any]:
        """
        Return a dictionary containing the agent's name, description, input types, and output types.

        Returns:
            Dict[str, Any]: A dictionary describing the agent's functionality and I/O types.
        """
        return {
            "name": self.name,
            "description": self.get_description_text(),
            "input_types": [t.__name__ for t in self.expected_input_types],
            "output_types": [t.__name__ for t in self.output_types]
        }

    @abstractmethod
    def get_description_text(self) -> str:
        """
        Return a natural language description of what this agent does.

        Returns:
            str: A description of the agent's functionality.
        """
        pass

    @abstractmethod
    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        """
        Process the input and return the result.

        Args:
            inputs (List[Any]): A list of inputs for the agent to process.
            output_file (str): The path to the output JSON file.

        Returns:
            List[Any]: The processed outputs.
        """
        pass


class NarrativeAgent(Agent):
    """
    An agent tasked with identifying the best single narrative from a source text,
    capturing the most information while focusing on the most interesting, human story.
    """

    def __init__(self, llm: llm.LLM):
        super().__init__(llm, "NarrativeAgent")
        self.expected_input_types = [infotypes.SourceText]
        self.output_types = [infotypes.Narrative]

    def get_description_text(self) -> str:
        return "I analyze source text to extract the most compelling and informative narrative, inspired by Ira Glass's storytelling approach."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file already exists
        if os.path.exists(output_file):
            print(f"Loading existing output from {output_file}")
            with open(output_file, 'r') as f:
                return [infotypes.Narrative(json.load(f)["narrative"])]

        source_text = inputs[0].value

        # Setup prompting and make call 
        system_prompt = """
        You are an expert storyteller and podcaster, embodying the style and approach of Ira Glass. 
        Your task is to analyze source text and extract the most compelling, top-level story, 
        focusing on the most interesting human elements while capturing the main point of the document.
        """
        user_prompt = f"""
        As an expert storyteller in the style of Ira Glass, your task is to analyze the following source text and create show notes for a potential podcast episode. 
       
        Here's the source text to work with:

        {source_text}
        
        Your output should include:

        1. A 2-3 paragraph summary that captures the essential idea of the podcast. This should:
           - Extract the main theme or central concept
           - Highlight the most interesting human story or element that illustrates this theme
           - Suggest a compelling way to introduce the topic and conclude it for a broader audience

        2. Key elements for storytelling:
           - An anecdote or detail that could make the audience laugh
           - A moment or aspect that could evoke emotion or make someone cry
           - An inspiring element or takeaway from the story
           - Any high-level anecdote ideas that could be developed further
           - A potential twist or unexpected angle to the story, if applicable

        3. Structure and tone:
           - Outline a clear narrative arc (beginning, middle, end) for the episode
           - Maintain a conversational tone, as if you're brainstorming ideas with a fellow producer
           - Suggest ways to make complex ideas accessible and interesting to a general audience

        Remember, these are show notes to guide the creation of a podcast episode, not the final script. Focus on capturing the essence of the story and providing a roadmap for further development.

        Please provide your carefully crafted show notes based on this text, keeping in mind Ira Glass's storytelling approach and the elements that make 'This American Life' episodes so compelling.
        """
        conversations = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        narrative = self.llm_call.call(conversations)

        output = {"narrative": narrative}
        # Save the output to a file
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        # Save prompt and response to a dev file
        with open(output_file + '_dev.txt', 'w') as f:
            f.write("Prompt:\n")
            f.write(json.dumps(conversations, indent=2))
            f.write("\n\nResponse:\n")
            f.write(narrative)

        return [infotypes.Narrative(narrative)]

class ActAgent(Agent):
    def __init__(self, llm: llm.LLM):
        super().__init__(llm, "ActAgent")
        self.expected_input_types = [infotypes.SourceText, infotypes.Narrative]
        self.output_types = [infotypes.Acts, infotypes.Acts, infotypes.Acts]

    def get_description_text(self) -> str:
        return "I create a detailed three-act structure for a podcast episode based on a narrative summary and source text."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            print("Loading acts from file")
            # If it does, load the acts from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                act_1 = output["act_1"]
                act_2 = output["act_2"]
                act_3 = output["act_3"]
        else:
            source_text, narrative = inputs[0].value, inputs[1].value

            # Setup prompting and make call 
            system_prompt = """
            You are an expert storyteller and podcast structure specialist, skilled in crafting compelling three-act narratives. 
            Your task is to take a source text and a narrative summary, and create a detailed three-act structure for a podcast episode.
            Focus on creating a captivating story arc that engages listeners from start to finish.
            """
            user_prompt = f"""
            As an expert in podcast structuring, your task is to create a three-act structure for a podcast episode based on the following source text and narrative summary:

            Source Text:
            {source_text}

            Narrative Summary:
            {narrative}
            
            Please provide a detailed three-act structure for the podcast episode. Each act should be 1-2 paragraphs long and include:

            1. Act 1 (Setup):
               - How to introduce the topic and grab the listener's attention
               - Key information or context to establish early on
               - A hook or question that will carry through the episode

            2. Act 2 (Confrontation/Main Body):
               - The core of the story or main ideas to explore
               - How to develop the narrative and deepen listener engagement
               - Any twists, turns, or key revelations to include

            3. Act 3 (Resolution):
               - How to bring the story to a satisfying conclusion
               - Key takeaways or insights for the audience
               - Any final thoughts or calls to action

            For each act, describe what should be included and how to tell the story effectively. Consider pacing, emotional beats, and how to maintain listener interest throughout the episode.

            Remember, this structure should serve as a guide for further script development, capturing the essence of the story and providing a clear roadmap for the podcast episode.

            IMPORTANT: Clearly separate each act with 'Act_1:', 'Act_2:', and 'Act_3:' labels. Do not include any other text outside of these acts.
            
            EXTREMEMLY IMPORTANT: The text you are reading is likely from a scientific paper - so the podcast should take that framing - i.e. the acts should be how the hosts introduce the idea, talk about the idea and concude the idea. 
            For example a good act 1 would introduce the idea of the paper in a fun way - then name the authors and institution that put out the paper
            Act 2 should go over the main details of the paper, while striving towards hitting on the narrative outlined above. 
            Act 3 should conclude saying how good and interesting the paper was, and offering up some insights etc as outlined in the narrative. 
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            acts_text = self.llm_call.call(conversations)

            # Split the text into three acts
            act_1 = acts_text.split('Act_1:')[1].split('Act_2:')[0].strip()
            act_2 = acts_text.split('Act_2:')[1].split('Act_3:')[0].strip()
            act_3 = acts_text.split('Act_3:')[1].strip()

            output = {"act_1": act_1, "act_2": act_2, "act_3": act_3}
            # Save the output to a file
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(acts_text)

        return [infotypes.Acts(act_1), infotypes.Acts(act_2), infotypes.Acts(act_3)]
    
class ContextualizeAgent(Agent):
    """
    Agent that contextualizes a single act with supporting details from the source text.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "ContextualizeAgent")
        self.expected_input_types = [infotypes.SourceText, infotypes.Acts]
        self.output_types = [infotypes.IndepthSummary]

    def get_description_text(self) -> str:
        return "Contextualizes a single act with supporting details from the source text."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            print("Loading contexts from file")
            # If it does, load the contextualized act from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                contextualized_act = output["contextualized_act"]
        else:
            source_text = inputs[0].value
            act = inputs[1].value

            # Setup prompting and make call 
            system_prompt = """
            You are an expert at analyzing and contextualizing information. Your task is to take a high-level idea (an act) and the source text, then provide supporting details that enrich and expand upon the act.
            """
            user_prompt = f"""
            Given the following source text and act, please provide a high-level idea (which may be a slightly refined version of the act) and supporting details from the source text.

            Source Text:
            {source_text}

            Act:
            {act}

            Please format your response as follows:
            High Level Idea: [Refined version of the act or the act itself if no refinement is necessary]

            Supporting Details:
            - [Detail 1]
            - [Detail 2]
            - [Detail 3]
            ...

            Ensure that the supporting details are key points from the source text that are relevant to and support the high-level idea.
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            contextualized_act = self.llm_call.call(conversations)

            # Save the output to a file
            output = {"contextualized_act": contextualized_act}
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(contextualized_act)

        return [infotypes.IndepthSummary(contextualized_act)]


class AnalogyAgent(Agent):
    """
    Agent that generates analogies to explain complex concepts in simpler terms.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "AnalogyAgent")
        self.expected_input_types = [infotypes.IndepthSummary]
        self.output_types = [infotypes.IndepthSummary]

    def get_description_text(self) -> str:
        return "Generates analogies to explain complex concepts in simpler terms for a general audience."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            print("Loading analogies from file")
            # If it does, load the analogies from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                analogies = output["analogies"]
            return [infotypes.IndepthSummary(analogies)]
            
        else:
            summary = inputs[0].value

            # Setup prompting and make call 
            system_prompt = """
            You are an expert at creating analogies to explain complex concepts. Your task is to take a detailed summary and create 5 analogies that break down the content into easily understandable terms for a general audience with no specialized knowledge of the domain.
            """
            user_prompt = f"""
            Given the following detailed summary, please create 5 analogies that explain the key concepts in simple, relatable terms. Provide your thought process for each analogy, and then list all 5 analogies at the end.

            Detailed Summary:
            {summary}

            Please format your response as follows:

            Thought Process:
            [Explanation of your approach and reasoning for each analogy]

            Analogies:
            1. [First analogy]
            2. [Second analogy]
            3. [Third analogy]
            4. [Fourth analogy]
            5. [Fifth analogy]

            Ensure that the analogies are clear, relatable, and help explain the complex concepts to someone with no specialized knowledge of the domain.
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            analogies = self.llm_call.call(conversations)

            # Prepend the original summary to the analogies
            full_response = f"Original Summary:\n{summary}\n\n{analogies}"

            # Save the output to a file
            output = {"analogies": full_response}
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(full_response)

            return [infotypes.IndepthSummary(full_response)]


class TranscriptAgent(Agent):
    """
    Agent that creates a podcast transcript based on three acts and their corresponding in-depth summaries.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "TranscriptAgent")
        self.expected_input_types = [infotypes.Acts, infotypes.IndepthSummary,
                                     infotypes.Acts, infotypes.IndepthSummary,
                                     infotypes.Acts, infotypes.IndepthSummary]
        self.output_types = [infotypes.Transcript]

    def get_description_text(self) -> str:
        return "Creates a podcast transcript between two hosts discussing a research paper based on three acts and their corresponding in-depth summaries."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            print("Loading transcripts from file")
            # If it does, load the transcript from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                transcript = output["transcript"]
        else:
            act1, summary1, act2, summary2, act3, summary3 = inputs

            # Setup prompting and make call 
            system_prompt = """
            You are an expert podcast scriptwriter for a show called "Mohonk Stories". Your task is to create an engaging, natural, and informative dialogue between two hosts, Carolyn and Bob, discussing a research paper. The hosts are friendly, smart, and funny. The conversation should last about 10 minutes when spoken aloud.
            """
            user_prompt = f"""
            Create a transcript for a "Mohonk Stories" podcast episode where hosts Carolyn and Bob discuss a research paper. Use the following three-act structure and in-depth summaries as guidance:

            Act 1: {act1.value}
            Summary 1: {summary1.value}

            Act 2: {act2.value}
            Summary 2: {summary2.value}

            Act 3: {act3.value}
            Summary 3: {summary3.value}

            Guidelines:
            1. Structure the discussion following the three-act format, using it to guide the flow of the conversation.
            2. Use information from the in-depth summaries to provide specific examples and details from the paper.
            3. Incorporate the best analogies provided in the summaries to explain complex concepts clearly.
            4. Make it clear that the hosts are discussing a research paper, not experiencing the events themselves.
            5. Inject personality and humor into the dialogue to make it engaging and entertaining.
            6. Ensure the transcript follows this format:
               Carolyn: [Carolyn's dialogue]
               Bob: [Bob's dialogue]

            Begin the transcript with a brief introduction to the show and end with a conclusion and sign-off.

            And all you should return is Carolyn: Bob: - no other explainer text etc. And do not add any "haha"s or other similar things.
            Or anything like (chuckles) just normal text. 

            The hosts should definitely, if possible, mention who the authors of the paper are and what institution they are from. 
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            transcript = self.llm_call.call(conversations)

            # Save the output to a file
            output = {"transcript": transcript}
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(transcript)

        return [infotypes.Transcript(transcript)]

class CombineTranscriptsAgent(Agent):
    """
    Agent that combines multiple transcripts into a single, cohesive podcast transcript.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "CombineTranscriptsAgent")
        self.expected_input_types = [infotypes.Transcript, infotypes.Transcript, infotypes.Transcript]
        self.output_types = [infotypes.Transcript]

    def get_description_text(self) -> str:
        return "Combines multiple transcripts into a single, cohesive podcast transcript."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            print("Loading combined podcast")
            # If it does, load the transcript from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                combined_transcript = output["transcript"]
        else:
            transcript1, transcript2, transcript3 = inputs[0].value, inputs[1].value, inputs[2].value

            # Setup prompting and make call 
            system_prompt = """
            You are an expert podcast editor, skilled in refining and polishing podcast transcripts.
            Your task is to take three slightly different versions of the same podcast episode transcript and merge them into one cohesive, well-structured final transcript.
            Focus on creating a seamless flow of information while maintaining the best elements from each input version.
            """
            user_prompt = f"""
            As an expert podcast editor, your task is to combine the following three versions of the same podcast episode transcript into a single, polished final version:

            Version 1:
            {transcript1}

            Version 2:
            {transcript2}

            Version 3:
            {transcript3}
            
            Please create a final transcript following these guidelines:

            1. Combine the best elements from all three versions into a single, flowing conversation.
            2. Ensure the final transcript is approximately the length of two of the input versions (i.e. we want it to be about double the length).
            3. Select the most insightful points and clearest explanations from each version.
            4. Smooth out any inconsistencies or repetitions between the different versions.
            5. Ensure the conversation remains engaging and natural throughout.
            6. Keep the existing host names consistent in the final transcript.
            7. Follow the standard transcript format:
               Host1: [Host1's dialogue]
               Host2: [Host2's dialogue]

            The goal is to create a single, polished podcast episode transcript that represents the best version of the conversation.

            Very important!!!
            The fromat should be 
            [Bob]: 
            [Carolyn]: 
            And their dialogue and nothing else, no "haha"s or things (chuckles) or anything like that just text. 

            And please make the dialogue pretty long - we are summarizing to 1, but it should be as long as all three combined. 
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            combined_transcript = self.llm_call.call(conversations)

            # Save the output to a file
            output = {"transcript": combined_transcript}
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(combined_transcript)

        return [infotypes.Transcript(combined_transcript)]


class PersonalizeAgent(Agent):
    """
    Agent that personalizes a podcast transcript using host information and adds human-like elements.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "PersonalizeAgent")
        self.expected_input_types = [infotypes.Transcript]
        self.output_types = [infotypes.Transcript]
        self.bob = hosts.Bob()
        self.carolyn = hosts.Carolyn()

    def get_description_text(self) -> str:
        return "Personalizes a podcast transcript using host information and adds human-like elements."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            print("Loading personalized transcript from file")
            # If it does, load the transcript from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                personalized_transcript = output["transcript"]
        else:
            transcript = inputs[0].value

            system_prompt = """
            You are an expert podcast editor, skilled in personalizing conversations and making them feel more natural and human.
            Your task is to take a podcast transcript and enhance it with personal details about the hosts and add human-like elements to the conversation.
            """

            user_prompt = f"""
            Please personalize and humanize the following podcast transcript:

            {transcript}

            Use the following information about the hosts:

            Bob: {self.bob.get_description()}
            Carolyn: {self.carolyn.get_description()}

            Guidelines for personalization:
            1. Add 2-3 lines of small talk at the beginning, referencing the hosts' interests or current events in New Paltz.
            2. Naturally transition from the small talk into the main topic.
            3. Where appropriate, inject further personal information about the hosts throughout the conversation.
            4. Vary line length and pacing. Include longer explanations from one host, followed by quick back-and-forths.
            5. Break up existing sentences with natural interruptions or brief interjections from the other host.
            6. Add brief verbal fillers like "Hm" or "Oh yeah" or "Uhh" to make the conversation feel more natural.
            7. Maintain the overall structure and content of the original transcript.
            8. Ensure the additions feel organic and don't disrupt the flow of information.
            9. Do not add any stage directions like [laughs] or [pauses].
            10. Focus on creating a natural, conversational rhythm with varied sentence structures and lengths.

            Very important: 
            This will be sent to a text to voice engine - so no adding of [chuckles] or anything like that! 

            EXTREMELY IMPORTANT: 
            This new output transcript should have long sequences like now but then also short breaks. Here is an example: All right, everybody, get ready for a deep dive today into something really cool. 

            [Carolyn]: Yeah. This one's wild. 

            [Bob]: We're talking generative agents and no, before you ask, not something we pulled from science fiction. 

            [Carolyn]: Though it kind of feels like it, right? We're talking AI agents, but like on a whole new level, actually simulating human behavior. 

            [Bob]: And when we say simulating, we mean believably, like really believably. And the best part is our source material, a brand new research paper straight out of Stanford and Google. 

            [Carolyn]: Fresh off the presses. 

            [Bob]: Mmmmm

            [Carolyn]: And these researchers did something really cool. They built like a virtual town, called it Smallville, populated it with these AI agents, and then they just let things play out.

            [Bob]: It's like they unleashed the AI equivalent of like a reality show or something. 

            [Carolyn]: There you go. Only instead of manufactured drama, we're talking about genuine emergent behavior. So picture the Sims, right? But instead of you controlling every move the characters make.

            [Bob]: Which let's be honest is how we all secretly play it anyway, right? 

            [Carolyn]: Maybe. But here, no micromanaging. These AI characters, they make their own choices based on their personalities, their relationships, everything you'd expect from, well, a real person. 

            [Bob]: It's the Sims, but with free will. What could possibly go wrong? But seriously, the level of detail in this research is mind blowing. They crafted 25 unique AI agents. And we're not just talking different outfits here. 

            [Carolyn]: Each one has a backstory, like full on where they go to school, what's their favorite color kind of backstories. 

            [Bob]: Quirks even. The researchers wanted to see if they could create a truly dynamic and complex society, not just a bunch of bots going through pre-programmed motions. 

            [Carolyn]: And that's the genius of it. So to really wrap our heads around this, let's zoom in on one of these AI residents. Let me introduce you to John Lin. 

            [Bob]: John Lin. All right. Tell us about him. 

            [Carolyn]: So John's a pharmacy owner in Smallville. And we get to see his whole day play out through these diary-like entries in the research paper.

            [Bob]: Hold on. So he's keeping a diary now. 

            [Carolyn]: Essentially. And it's fascinating to get these little glimpses into his thought process, his interactions, even what he had for breakfast. 

            [Bob]: I'm already more invested in this AI than some of the people I went to high school with. OK. So what's John up to? Spill the tea. 

            [Carolyn]: So John starts his day like anyone else, right? Wakes up, has breakfast with the family, even remembers little details from that conversation later on in the day. 

            [Bob]: Wait. Hold up. Nobody programmed him to remember those details. 

            [Carolyn]: Nope. And that's what's so cool about this. The researchers call it emergent behavior. Those specific interactions. Nobody scripted them. They emerged organically from the way these AI agents process information and make decisions. 

            [Bob]: So it's like they're improvising based on what they've learned. That's both impressive and kind of terrifying. 

            [Carolyn]: A little bit of both. 

            [Bob]: Yeah. 

            [Carolyn]: But that's what makes them generative agents. They're not just reacting to pre-programmed cues. They're actively creating new situations, new relationships, even new problems probably. 

            [Bob]: Oh, I'm sure there's drama in Smallville. You know what they say? Small town, big AI drama. But this is huge. It's not just about mimicking human behavior. It's about replicating the systems that drive that behavior in the first place. 

            [Carolyn]: Exactly. And that's where things get really, really interesting. 

            Obviously keep the core story the same, but try to match this pacing and style!


            """

            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            personalized_transcript = self.llm_call.call(conversations)

            # Save the output to a file
            output = {"transcript": personalized_transcript}
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(personalized_transcript)

        return [infotypes.Transcript(personalized_transcript)]


class DoubleTranscriptAgent(Agent):
    """
    Agent that takes a transcript and doubles its length.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "DoubleTranscriptAgent")
        self.expected_input_types = [infotypes.Transcript]
        self.output_types = [infotypes.Transcript]

    def get_description_text(self) -> str:
        return "Takes a transcript and doubles its length while maintaining the original content and style."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            # If it does, load the transcript from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                doubled_transcript = output["transcript"]
        else:
            original_transcript = inputs[0].value

            # Setup prompting and make call 
            system_prompt = """
            You are an expert podcast editor, skilled in expanding and elaborating on existing content.
            Your task is to take a podcast transcript and double its length while maintaining the original content, style, and flow of the conversation.
            Focus on adding more details, examples, and natural dialogue to enhance the existing discussion.
            """
            user_prompt = f"""
            As an expert podcast editor, your task is to double the length of the following podcast transcript:

            {original_transcript}
            
            Please create an expanded version of the transcript following these guidelines:

            1. Maintain the original content, style, and flow of the conversation.
            2. Add more details, examples, and explanations to existing points.
            3. Expand on ideas and concepts mentioned in the original transcript.
            4. Insert additional relevant questions and responses to deepen the discussion.
            5. Ensure the expanded transcript is approximately twice the length of the original.
            6. Keep the existing host names and transcript format:
               [Host1]: [Host1's dialogue]
               [Host2]: [Host2's dialogue]

            The goal is to create a more in-depth and comprehensive version of the original conversation while preserving its essence and style.
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            doubled_transcript = self.llm_call.call(conversations)

            # Save the output to a file
            output = {"transcript": doubled_transcript}
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(doubled_transcript)

        return [infotypes.Transcript(doubled_transcript)]


class SimpleTranscriptAgent(Agent):
    """
    Agent that converts the three-act structure into a simple podcast transcript between two people.
    """

    def __init__(self, llm_call: llm.LLM):
        super().__init__(llm_call, "SimpleTranscriptAgent")
        self.expected_input_types = [infotypes.Acts]
        self.output_types = [infotypes.Transcript]

    def get_description_text(self) -> str:
        return "Converts a three-act structure into a simple podcast transcript between two hosts."

    def run(self, inputs: List[Any], output_file: str) -> List[Any]:
        # Check if output file exists
        if os.path.exists(output_file):
            # If it does, load the transcript from the file
            with open(output_file, 'r') as f:
                output = json.load(f)
                transcript = output["transcript"]
        else:
            acts = inputs[0].value

            # Setup prompting and make call 
            system_prompt = """
            You are an expert podcast scriptwriter, skilled in creating engaging conversations between two hosts.
            Your task is to take a three-act structure and convert it into a natural, flowing conversation for a podcast episode.
            Focus on creating a dynamic and engaging dialogue that brings the content to life.
            """
            user_prompt = f"""
            As an expert podcast scriptwriter, your task is to create a transcript for a podcast episode based on the following three-act structure:

            {acts}
            
            Please write a transcript for the podcast episode with the following guidelines:

            1. The conversation should be between two hosts: Alex and Sam.
            2. Create a natural, flowing dialogue that covers all the key points from each act.
            3. Include appropriate transitions between acts.
            4. Add personality and chemistry between the hosts to make the conversation engaging.
            5. Ensure the transcript follows this format:
               Alex: [Alex's dialogue]
               Sam: [Sam's dialogue]

            Remember to maintain the story arc and key elements from the three-act structure while making it conversational and engaging for listeners.
            """
            conversations = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            transcript = self.llm_call.call(conversations)

            output = {"transcript": transcript}
            # Save the output to a file
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)

            # Save prompt and response to a dev file
            with open(output_file + '_dev.txt', 'w') as f:
                f.write("Prompt:\n")
                f.write(json.dumps(conversations, indent=2))
                f.write("\n\nResponse:\n")
                f.write(transcript)

        return [infotypes.Transcript(transcript)]
