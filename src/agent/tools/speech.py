import os
import sys
from functools import partial
from typing import List
from agent.base import ChatMessage
from steamship import Steamship, SteamshipError, Block
from termcolor import colored
from api import GirlfriendGPT
from nyan import nyan
from speech import GenerateSpeechTool

class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def show_results(response_messages: List[Block]):
    print(colored("\nResults: ", "blue", attrs=["bold"]))
    for message in response_messages:
        print(message.url if message.mime_type else message.text, end="\n\n")


def main():
    Steamship()

    with Steamship.temporary_workspace() as client:
        # Create an instance of the GenerateSpeechTool
        speech_tool = GenerateSpeechTool(
            client=client,
            voice_id="21m00Tcm4TlvDq8ikWAM",
            elevenlabs_api_key="YOUR_ELEVENLABS_API_KEY"
        )

        run = partial(
            run_agent,
            agent=GirlfriendGPT(
                client=client,
                config={
                    "bot_token": "6243114810:AAHNzDglQhZ_GjKrAzrZgCygb2kmwb92kCE",
                    "personality": "nyan",
                },
            ),
            speech_tool=speech_tool
        )

        print(f"Starting Agent...")
        print("If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n")

        while True:
            prompt = input(colored(f"Prompt: ", "blue"))
            run(prompt=prompt)


def run_agent(agent, prompt: str, speech_tool: GenerateSpeechTool) -> None:
    message = ChatMessage(text=prompt, chat_id="123")
    response = agent.create_response(incoming_message=message)
    show_results(response)

    # Use the speech tool to generate speech from the response
    speech_id = speech_tool.run(response.text)  # Modify this line based on your response object

    # Add any additional code or logic you need

if __name__ == "__main__":
    # When running locally, we can use print statements to capture logs / info.
    # As a result, we will disable python logging to run. This will keep the output cleaner.
    with LoggingDisabled():
        try:
            main()
        except SteamshipError as e:
            print(colored("Aborting! ", "red"), end="")
            print(f"There was an error encountered when running: {e}")
