import pandas as pd
import os
from dotenv import load_dotenv

import openai
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import (
    AIMessage, 
    HumanMessage, 
    SystemMessage, 
    ChatGeneration
)
from langchain import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)

from langchain.output_parsers import (
    StructuredOutputParser,
    ResponseSchema
)

import prompt_templates

class CommentAnalyzer:

    llm: AzureChatOpenAI
    comment: str
    format_instructions: str
    chat_prompt_template: ChatPromptTemplate
    output_parser: StructuredOutputParser
    reponse_schema_fiels_count: int

    def __init__(self):
        
        load_dotenv()
        openai.api_type = "azure"
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        self.llm = AzureChatOpenAI(
            openai_api_base = os.getenv("OPENAI_API_BASE"),
            openai_api_version = "2023-05-15",
            deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME"),
            openai_api_key = os.getenv("OPENAI_API_KEY"),
            openai_api_type = "azure",
            request_timeout = 15,
            temperature = 0
        ) # type: ignore

        # Define prompts
        system_message_prompt_template = SystemMessagePromptTemplate.from_template(prompt_templates.SYSTEM_MESSAGE_PROMPT_TEMPLATE)
        human_message_prompt_template = HumanMessagePromptTemplate.from_template(prompt_templates.HUMAN_MESSAGE_PROMPT_TEMPLATE)
        self.chat_prompt_template = ChatPromptTemplate.from_messages([
            system_message_prompt_template,
            human_message_prompt_template
        ])

        # Generate response format instructions
        response_schema = []
        for response_field_name, response_field_desc in prompt_templates.RESPONSE_SCHEMA.items():
            response_schema.append(
                ResponseSchema(
                    name=response_field_name,
                    description=response_field_desc
                ))
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schema)
        self.format_instructions = self.output_parser.get_format_instructions()
        # print(format_instructions)
        self.reponse_schema_fiels_count = len(response_schema)

    def analyze(self, 
                social_media_channel: str, 
                company: str, 
                product: str, 
                product_description: str,
                comment: str):
        # Format the final template
        chat_prompt = self.chat_prompt_template.format_prompt(
                social_media_channel=social_media_channel,
                company=company,
                product=product,
                product_description=product_description,
                comment=comment,
                format_instructions=self.format_instructions
        )

        # generate output from LLM
        try:
            model_output = self.llm(
                chat_prompt.to_messages(),
            )
            
            return self.output_parser.parse(model_output.content)

        except Exception as e:
            print(e)
            return None
