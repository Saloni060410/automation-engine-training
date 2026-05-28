import os
import json
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash"]

SYSTEM_PROMPT = (
    "You are a workflow planner. Given a user command, return a workflow as a list of steps "
    "using ONLY these components: email_reader, pdf_parser, llm_extractor, validator, api_caller.\n"
    "Component descriptions:\n"
    "- email_reader: reads and fetches emails\n"
    "- pdf_parser: parses any document or file (PDF, Excel, CSV, etc.)\n"
    "- llm_extractor: extracts, compares, or analyzes text using an LLM\n"
    "- validator: validates data against business rules\n"
    "- api_caller: sends data to an external system or API\n"
    "Always return at least one step. Map the command to the closest available components."
)

# Tool definition for Gemini function-calling
CREATE_WORKFLOW_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="create_workflow",
            description="Return a workflow as a list of steps for the given user command.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "steps": types.Schema(
                        type="ARRAY",
                        items=types.Schema(
                            type="OBJECT",
                            properties={
                                "step": types.Schema(
                                    type="INTEGER",
                                    description="Step number starting from 1"
                                ),
                                "component": types.Schema(
                                    type="STRING",
                                    enum=[
                                        "email_reader",
                                        "pdf_parser",
                                        "llm_extractor",
                                        "validator",
                                        "api_caller"
                                    ],
                                    description="Component to use for this step"
                                ),
                                "params": types.Schema(
                                    type="OBJECT",
                                    description="Parameters passed to the component"
                                )
                            },
                            required=["step", "component", "params"]
                        )
                    )
                },
                required=["steps"]
            )
        )
    ]
)


def parse_command(command: str) -> list:
    prompt = f"{SYSTEM_PROMPT}\n\nUser command: {command}"

    for model in MODELS:
        print(f"Trying model: {model}")
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[CREATE_WORKFLOW_TOOL],
                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(mode="ANY")
                    )
                )
            )

            function_call = None
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call = part.function_call
                    break

            if function_call is None:
                raise ValueError(
                    f"LLM did not return a function call. Raw response: {response.text}"
                )

            args = dict(function_call.args)
            steps = args.get("steps")

            if not isinstance(steps, list) or len(steps) == 0:
                raise ValueError(f"Expected a non-empty list of steps, got: {args}")

            steps = [dict(s) for s in steps]

            for step in steps:
                if not all(k in step for k in ("step", "component", "params")):
                    raise ValueError(f"Step missing required fields: {step}")

            return steps

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"Quota exhausted for {model}, trying next model...")
                continue
            raise

    raise Exception("All models exhausted. Check your API key or wait until quota resets.")


if __name__ == "__main__":
    print("Workflow Engine — type a command or 'quit' to exit\n")

    while True:
        command = input("Enter command: ").strip()

        if not command:
            continue
        if command.lower() == "quit":
            break

        print()
        workflow = parse_command(command)
        print("\nWorkflow:")
        print(json.dumps(workflow, indent=2))
        print()
