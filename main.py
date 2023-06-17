import os
import sys
import logging
from functools import partial
from typing import List
from agent.base import ChatMessage
from steamship import Steamship, SteamshipError, Block
from termcolor import colored

# Import the necessary module for Generator
from steamship.plugins.generator import Generator

from nyan import nyan


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
        # Create an instance of the Generator plugin
        generator = client.use_plugin("gpt-4")

        run = partial(
            run_agent,
            agent=GirlfriendGPT(
                client=client,
                config={
                    "bot_token": "6243114810:AAHNzDglQhZ_GjKrAzrZgCygb2kmwb92kCE",
                    "personality": "nyan",
                },
            ),
            generator=generator,
        )
        print(f"Starting Agent...")
        print(
            f"If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
        )
        while True:
            prompt = input(colored(f"Prompt: ", "blue"))
            run(
                prompt=prompt,
            )


def run_agent(agent, generator, prompt: str) -> None:
    message = ChatMessage(text=prompt, chat_id="123")
    response = agent.create_response(incoming_message=message)
    show_results(response)

    # Generate text using the Generator plugin
    task = generator.generate(text=prompt)
    task.wait()

    # Access the generated output
    output_text = task.output.blocks[0].text
    print(output_text)


if __name__ == "__main__":
    # when running locally, we can use print statements to capture logs / info.
    # as a result, we will disable python logging to run. this will keep the output cleaner.
    with LoggingDisabled():
        try:
            main()
        except SteamshipError as e:
            print(colored("Aborting! ", "red"), end="")
            print(f"There was an error encountered when running: {e}")
