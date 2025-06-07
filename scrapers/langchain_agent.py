import os
from typing import List, Dict, Any, Optional
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
import re
from datetime import datetime
from grocery_scraper import GroceryScraper
import json
from pathlib import Path

# Set up the scraper
scraper = GroceryScraper(use_proxy=True)

# Set up the LLM - Using Ollama with Mistral (run locally)
# First install Ollama from https://ollama.ai/ then run: ollama pull mistral
llm = Ollama(model="mistral", temperature=0.1)

# Alternatively, use HuggingFace Inference API (requires API key)
# from getpass import getpass
# HUGGINGFACEHUB_API_TOKEN = getpass()
# os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
# llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2")

# Define the tools that our agent can use
def scrape_website(url: str) -> str:
    """Scrape a website for grocery prices"""
    try:
        results = scraper.scrape_grocery_prices(url)
        if not results:
            return "No products found on this page."
        
        # Save the results
        filename = f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = scraper.save_results(results, filename)
        
        # Format the results for the LLM
        formatted = []
        for item in results[:10]:  # Limit to first 10 items
            formatted.append(f"- {item['name']}: {item['price']} (Source: {item['source']})")
        
        return f"Found {len(results)} products. First few items:\n" + "\n".join(formatted)
    except Exception as e:
        return f"Error scraping website: {str(e)}"

def analyze_price_trends(products: List[Dict[str, Any]]) -> str:
    """Analyze price trends from scraped data"""
    if not products:
        return "No product data available for analysis."
    
    # Simple analysis - in a real app, you'd use pandas/numpy
    prices = []
    for p in products:
        try:
            # Extract numeric price
            price_str = re.sub(r'[^\d.]', '', p.get('price', '0'))
            if price_str:
                prices.append(float(price_str))
        except (ValueError, TypeError):
            continue
    
    if not prices:
        return "No valid price data found for analysis."
    
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    
    return (
        f"Price Analysis (based on {len(products)} products):\n"
        f"- Average Price: ${avg_price:.2f}\n"
        f"- Minimum Price: ${min_price:.2f}\n"
        f"- Maximum Price: ${max_price:.2f}"
    )

# Set up the tools
tools = [
    Tool(
        name="scrape_website",
        func=scrape_website,
        description="Useful when you need to scrape grocery prices from a website. "
                  "Input should be a valid URL."
    ),
    Tool(
        name="analyze_prices",
        func=analyze_price_trends,
        description="Useful when you need to analyze price trends from scraped data. "
                  "Input should be a list of product dictionaries with 'price' keys."
    )
]

# Set up the prompt template
class CustomPromptTemplate(StringPromptTemplate):
    template = """You are a helpful AI assistant for grocery price monitoring. Your goal is to help users track and analyze grocery prices.
    
    You have access to the following tools:
    {tools}
    
    Use the following format:
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    {agent_scratchpad}"""

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        intermediate_steps = kwargs.pop("intermediate_steps", [])
        thoughts = ""
        
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        
        # Set the agent_scratchpad parameter to be the thoughts so far
        kwargs["agent_scratchpad"] = thoughts
        
        # Format the tools and tool_names
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        
        return self.template.format(**kwargs)

# Set up the output parser
class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> AgentAction or AgentFinish:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        
        # Parse the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
            
        action = match.group(1).strip()
        action_input = match.group(2).strip().strip('"\'')
        
        return AgentAction(tool=action, tool_input=action_input, log=llm_output)

# Initialize the agent
prompt = CustomPromptTemplate(
    tools=tools,
    input_variables=["input", "intermediate_steps"]
)

output_parser = CustomOutputParser()

llm_chain = LLMChain(llm=llm, prompt=prompt)

tool_names = [tool.name for tool in tools]

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=tool_names,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
)

def run_agent(query: str) -> str:
    """Run the agent with a user query"""
    try:
        result = agent_executor.run(query)
        return result
    except Exception as e:
        return f"Error running agent: {str(e)}"

if __name__ == "__main__":
    # Example usage
    queries = [
        "Scrape prices from https://www.walmart.com/cp/food/976759",
        "What's the average price of eggs in the scraped data?",
        "Compare prices between different sources"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        result = run_agent(query)
        print(f"\nResult: {result}")
        print("=" * 50)
