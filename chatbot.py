import sys
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
import vnquant.data as dt
import datetime
import pandas as pd
from typing_extensions import TypedDict

current_path = os.getcwd()
sys.path.append(current_path)

class QuantInput(BaseModel):
    symbol: str = Field(..., description="Stock symbol to look up")

class Quant(BaseModel):
    symbol: str
    latest_date: str 
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int

class MultiAgentState(TypedDict):
    query: str
    query_type: str
    symbol: str  # Added symbol field
    response: str

@tool(args_schema=QuantInput)
def quant_last_price_tool(symbol: str) -> QuantInput:
    """Return Quant information"""
    try:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
        
        loader = dt.DataLoader(
            symbols=[symbol.upper()],
            start=start_date,
            end=end_date,
            table_style='stack',
        )
        
        df = loader.download()
        
        if df.empty:
            return Quant(
                symbol=symbol,
                latest_date="N/A",
                open_price=0,
                close_price=0,
                high_price=0,
                low_price=0,
                volume=0,
            )
        
        latest = df.reset_index().sort_values('date').iloc[-1]
        return Quant(
            symbol=latest['code'],
            latest_date=latest['date'].strftime('%Y-%m-%d'),
            open_price=latest['open'],
            close_price=latest['close'],
            high_price=latest['high'],
            low_price=latest['low'],
            volume=int(latest['volume_match']),
        )
        
    except Exception as e:
        return Quant(
                symbol=symbol,
                latest_date="N/A",
                open_price=0,
                close_price=0,
                high_price=0,
                low_price=0,
                volume=0,
            )

class ChatBot:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=120,
            max_retries=2,
        )
        
        self.builder = StateGraph(MultiAgentState)
        self._build_graph()
        self.graph = self.builder.compile()

    def _build_graph(self):
        self.builder.add_node("router", self.router_node)
        self.builder.set_entry_point("router")
        self.builder.add_node('quant_last_price', self.quant_last_price_node)
        self.builder.add_node('general_assistant', self.general_assistant_node)
        
        self.builder.add_conditional_edges(
            "router",
            self.route_query,
            {
                'GENERAL': 'general_assistant',
                'QUANT': 'quant_last_price'
            }
        )
        
        self.builder.add_edge('quant_last_price', END)
        self.builder.add_edge('general_assistant', END)

    def router_node(self, state: MultiAgentState):
        query_category_prompt = """
        You are an expert in categorizing user queries for proper routing.
        Categories:
        - QUANT: Question relate to Stock.
        - GENERAL: Static knowledge, definitions, explanations, or questions about well-established facts (e.g., historical facts, math, theoretical concepts)
        Return only one word: QUANT or GENERAL.
        """
        messages = [
            SystemMessage(content=query_category_prompt),
            HumanMessage(content=state['query'])
        ]
        response = self.model.invoke(messages)
        return {"query_type": response.content.strip()}
    
    def quant_last_price_node(self, state: MultiAgentState):
        extract_prompt = """
        You are an expert in identifying the symbols of the stocks in question.
        Return only symbol in word.
        For example: Query: Tell me the latest price of stock code FPT.
        Return: FPT
        """
        messages = [
            SystemMessage(content=extract_prompt),
            HumanMessage(content=state['query'])
        ]
        response = self.model.invoke(messages)
        state['symbol'] = response.content.strip().upper()

        ## Search
        search_prompt = f"""
        You are a stock market analyst. Transform the raw stock data into natural language, matching the language of the response with {state['query']} using the following template:
        **Formatting rules:**
        1. Date format: DD/MM/YYYY
        2. Currency: Treat numbers with a decimal point as representing thousands (e.g., 153.4 means 153,400). Multiply the input by 1,000 , format the result with commas as thousands separators, and add "VND" at the end (e.g., 40.4 → 40,400 VND).
        3. Volume: Format with commas + "shares traded"
        3. Always start with "[Market Update]"
        """
        quant_data = quant_last_price_tool.invoke({"symbol": state['symbol']})
        messages = [
            SystemMessage(content=search_prompt),
            HumanMessage(content=f"""
            Query: {state['query']}             
            Symbol: {quant_data.symbol}
            Date: {quant_data.latest_date}
            Opening Price: {quant_data.open_price}
            Closing Price: {quant_data.close_price}
            High Price: {quant_data.high_price}
            Low Price: {quant_data.low_price}
            Volume: {quant_data.volume}
            """)
        ]

        response = self.model.invoke(messages)
        return {'response': response.content}

    def general_assistant_node(self, state: MultiAgentState):
        prompt = """
        You're a friendly assistant and your goal is to answer general questions in Vietnamese.
        Please don't provide any unchecked information;
        Just say that you don't know if you don't have enough information.
        """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=state['query'])
        ]
        response = self.model.invoke(messages)
        return {"response": response.content}

    def route_query(self, state: MultiAgentState):
        return state['query_type']

    def process_query(self, query: str):
        input_data = {
            'query': query,
            'query_type': "",
            'symbol': "",
            'response': ""
        }
        output = self.graph.invoke(input_data)
        return output

if __name__ == "__main__":
    chatbot = ChatBot()
    print("Enter your message (type 'exit' to quit):")
    
    while True:
        try:
            query = input("\033[1m User >>:\033[0m ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("Chatbot: Goodbye!")
                break
                
            output = chatbot.process_query(query)
            print(f"\nChatbot: {output['response']}\n")
            print("="*80)
            
        except KeyboardInterrupt:
            print("\nChatbot: Session ended.")
            break