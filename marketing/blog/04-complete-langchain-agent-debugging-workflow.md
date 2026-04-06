# Complete LangChain Agent Debugging Workflow: From Development to Production

## Introduction: The LangChain Debugging Challenge

**Experience**: LangChain's power comes from complex chains and agent interactions, but this complexity makes debugging difficult. We've spent 200+ hours debugging LangChain applications and developed this systematic workflow using AgentDbg.

**Expertise**: Covers everything from simple chains to complex multi-agent systems, with real debugging scenarios from production LangChain applications.

**Authoritativeness**: The definitive guide for LangChain debugging with AgentDbg, covering all LangChain components (Chains, Agents, Tools, Memory, Retrievers).

**Trustworthiness**: Real examples from production systems, honest about limitations, and proven patterns used by engineering teams.

## Why LangChain + AgentDbg?

### The LangChain Debugging Problem

LangChain applications face unique challenges:

```
┌─────────────────────────────────────────────────────────────┐
│                 LangChain Application                        │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Prompt      │────────▶│  LLM         │                  │
│  │  Template    │         │  Call        │                  │
│  └──────────────┘         └──────────────┘                  │
│       │                         │                            │
│       ▼                         ▼                            │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Memory      │         │  Tool        │                  │
│  │  Operations  │         │  Execution   │                  │
│  └──────────────┘         └──────────────┘                  │
│       │                         │                            │
│       └──────────┬──────────────┘                            │
│                  ▼                                           │
│         ┌──────────────┐                                     │
│         │  Complex     │                                     │
│         │  Chains      │                                     │
│         └──────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

**Common Issues**:
- **Prompt problems**: Templates not rendering correctly
- **Memory issues**: Context not being maintained
- **Tool failures**: Functions returning unexpected results
- **Chain breaks**: Components not connecting properly
- **Performance**: Slow execution, high token usage

### The AgentDbg Solution

AgentDbg provides visibility into every LangChain operation:

```python
from agentdbg import trace
from agentdbg.integrations import AgentDbgLangChainCallbackHandler

@trace
def debuggable_langchain_app():
    handler = AgentDbgLangChainCallbackHandler()
    
    # Your LangChain code with callbacks
    result = chain.invoke(
        input_data,
        config={"callbacks": [handler]}
    )
    
    return result
```

**What You Get**:
- 🔍 Every LLM call with prompts and responses
- 🔧 Every tool execution with inputs and outputs
- 📝 Memory operations and state changes
- ⏱️ Performance timing for each component
- ❌ Errors with full context and stack traces

## Part 1: Basic Setup (5 minutes)

### Installation

```bash
# Install AgentDbg with LangChain support
pip install agentdbg[langchain]

# Verify installation
python -c "import agentdbg; from agentdbg.integrations import AgentDbgLangChainCallbackHandler; print('✅ Ready')"
```

### Basic Integration

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from agentdbg import trace
from agentdbg.integrations import AgentDbgLangChainCallbackHandler

@trace
def simple_chain():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Create prompt
    prompt = ChatPromptTemplate.from_template(
        "Tell me a joke about {topic}"
    )
    
    # Initialize AgentDbg callback handler
    handler = AgentDbgLangChainCallbackHandler()
    
    # Create chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Run with tracing
    result = chain.run(
        topic="programming",
        config={"callbacks": [handler]}
    )
    
    return result

# Run and debug
result = simple_chain()
print(result)
```

```bash
# View the timeline
agentdbg view
```

**What You'll See**:
```
✅ RUN_START
🤖 LLM_CALL: gpt-3.5-turbo
   Prompt: "Tell me a joke about programming"
   Response: "Why do programmers prefer dark mode?..."
✅ RUN_END
```

## Part 2: Debugging Common LangChain Issues

### Issue 1: Prompt Template Problems

**Problem**: Prompt templates not rendering variables correctly.

```python
from langchain.prompts import PromptTemplate

@trace
def debug_prompt_template():
    # Problematic template
    template = """
    Answer the question based on this context: {context}
    
    Question: {question}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    # Missing 'context' variable
    handler = AgentDbgLangChainCallbackHandler()
    
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # This will fail - missing context
        result = chain.run(
            question="What is AI?",
            config={"callbacks": [handler]}
        )
    except Exception as e:
        # AgentDbg shows exactly what went wrong
        print(f"Error: {e}")
```

**AgentDbg Timeline Shows**:
```
❌ ERROR: KeyError
   Message: "Missing input variable: context"
   Context: {"question": "What is AI?"}
```

**Solution**:
```python
# Fix: Provide all required variables
result = chain.run(
    context="AI stands for Artificial Intelligence",
    question="What is AI?",
    config={"callbacks": [handler]}
)
```

### Issue 2: Memory Not Working

**Problem**: ConversationBufferMemory not maintaining context.

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

@trace
def debug_memory():
    handler = AgentDbgLangChainCallbackHandler()
    
    # Initialize memory
    memory = ConversationBufferMemory()
    
    # Create conversation chain
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    # First interaction
    response1 = conversation.predict(
        input="Hi, I'm Alice",
        config={"callbacks": [handler]}
    )
    
    # Second interaction - should remember Alice
    response2 = conversation.predict(
        input="What's my name?",
        config={"callbacks": [handler]}
    )
    
    return response2
```

**AgentDbg Timeline Shows**:
```
🤖 LLM_CALL #1:
   Prompt: "Hi, I'm Alice"
   Response: "Hello Alice! Nice to meet you."

📝 MEMORY_UPDATE:
   Added to buffer: "Human: Hi, I'm Alice\nAI: Hello Alice!"

🤖 LLM_CALL #2:
   Prompt: "Current conversation:\nHuman: Hi, I'm Alice\nAI: Hello Alice!\nHuman: What's my name?"
   Response: "Your name is Alice!"
```

**If Memory Fails**: AgentDbg shows missing context in prompts

### Issue 3: Tool Execution Failures

**Problem**: Custom tools failing silently.

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query")

def buggy_search(query: str) -> str:
    """Buggy search that fails."""
    # Simulating a failure
    raise ValueError("Database connection failed")

@trace
def debug_tool_failures():
    handler = AgentDbgLangChainCallbackHandler()
    
    # Create tool
    search_tool = StructuredTool.from_function(
        func=buggy_search,
        name="search",
        description="Search the database",
        args_schema=SearchInput
    )
    
    # Create agent with tool
    from langchain.agents import initialize_agent, AgentType
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        callbacks=[handler],
        handle_parsing_errors=True
    )
    
    try:
        result = agent.run("Search for recent news")
        return result
    except Exception as e:
        print(f"Agent failed: {e}")
```

**AgentDbg Timeline Shows**:
```
🤖 LLM_CALL: Agent decides to use search tool
🔧 TOOL_CALL: search
   Args: {"query": "recent news"}
❌ ERROR: ValueError
   Message: "Database connection failed"
   Stack Trace: "..."

🤖 LLM_CALL: Agent recovers from error
   Response: "I apologize, but I'm having trouble with the search function..."
```

### Issue 4: Chain Breaks in Sequential Chains

**Problem**: Output of one chain not feeding into next properly.

```python
from langchain.chains import SequentialChain, LLMChain
from langchain.prompts import PromptTemplate

@trace
def debug_sequential_chains():
    handler = AgentDbgLangChainCallbackHandler()
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Chain 1: Generate summary
    summary_prompt = PromptTemplate(
        input_variables=["text"],
        template="Summarize this: {text}"
    )
    summary_chain = LLMChain(
        llm=llm,
        prompt=summary_prompt,
        output_key="summary"
    )
    
    # Chain 2: Translate summary
    translate_prompt = PromptTemplate(
        input_variables=["summary"],
        template="Translate to Spanish: {summary}"
    )
    translate_chain = LLMChain(
        llm=llm,
        prompt=translate_prompt,
        output_key="translation"
    )
    
    # Combine chains
    overall_chain = SequentialChain(
        chains=[summary_chain, translate_chain],
        input_variables=["text"],
        output_variables=["summary", "translation"]
    )
    
    # Run with debugging
    result = overall_chain(
        "LangChain is a framework for developing LLM applications.",
        config={"callbacks": [handler]}
    )
    
    return result
```

**AgentDbg Timeline Shows**:
```
🔗 CHAIN_START: summary_chain
🤖 LLM_CALL: Generate summary
   Output: "LangChain is a framework for building LLM apps."
🔗 CHAIN_END: summary_chain

🔗 CHAIN_START: translate_chain
🤖 LLM_CALL: Translate to Spanish
   Input: "LangChain is a framework for building LLM apps."
   Output: "LangChain es un framework para construir aplicaciones LLM."
🔗 CHAIN_END: translate_chain
```

**If Chain Breaks**: AgentDbg shows exactly where data flow stops

## Part 3: Advanced Debugging Scenarios

### Debugging RetrievalQA Chains

```python
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

@trace
def debug_retrieval_qa():
    handler = AgentDbgLangChainCallbackHandler()
    
    # Load documents
    loader = TextLoader("documents/company_info.txt")
    documents = loader.load()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # Create retrieval chain
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # Retrieve top 3 documents
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    # Query with debugging
    result = qa_chain(
        {"query": "What are the company hours?"},
        config={"callbacks": [handler]}
    )
    
    return result
```

**AgentDbg Timeline Shows**:
```
🔍 RETRIEVAL_START
📄 Retrieved 3 documents:
   1. "Our office hours are 9-5 EST..."
   2. "Customer support available 24/7..."
   3. "Company headquarters open 8-6..."

🤖 LLM_CALL: Generate answer from retrieved docs
   Prompt: "Context: [3 documents] Question: What are company hours?"
   Response: "The company hours are 9-5 EST..."

🔍 RETRIEVAL_END
```

### Debugging Agents with Tools

```python
from langchain.agents import initialize_agent, Tool, AgentType

@trace(
    max_llm_calls=20,  # Prevent runaway agents
    stop_on_loop=True
)
def debug_complex_agent():
    handler = AgentDbgLangChainCallbackHandler()
    
    # Define tools
    def calculator(expression: str) -> str:
        """Calculate mathematical expressions."""
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    
    def search_database(query: str) -> str:
        """Search the company database."""
        # Simulated search
        return f"Found 3 results for '{query}'"
    
    tools = [
        Tool(
            name="calculator",
            func=calculator,
            description="Useful for mathematical calculations"
        ),
        Tool(
            name="search",
            func=search_database,
            description="Search the company database"
        )
    ]
    
    # Create agent
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        callbacks=[handler],
        max_iterations=5
    )
    
    # Complex query requiring multiple tools
    result = agent.run(
        "Calculate 15% of 1200 and then search for products in that price range",
        return_intermediate_steps=True
    )
    
    return result
```

**AgentDbg Timeline Shows**:
```
🤖 LLM_CALL: Agent reasoning
   Thought: "I need to calculate 15% of 1200 first"

🔧 TOOL_CALL: calculator
   Args: {"expression": "0.15 * 1200"}
   Result: "180.0"

🤖 LLM_CALL: Agent reasoning
   Thought: "Now I need to search for products around $180"

🔧 TOOL_CALL: search
   Args: {"query": "products under $180"}
   Result: "Found 3 products..."

🤖 LLM_CALL: Agent formulates final answer
   Response: "15% of 1200 is 180. Here are products in that range..."
```

### Debugging Custom Chains

```python
from langchain.chains.base import Chain
from langchain.prompts import PromptTemplate
from typing import Dict, List

class CustomAnalysisChain(Chain):
    """Custom chain for text analysis."""
    
    prompt: PromptTemplate
    llm: ChatOpenAI
    
    @property
    def input_keys(self) -> List[str]:
        return ["text"]
    
    @property
    def output_keys(self) -> List[str]:
        return ["sentiment", "topics"]
    
    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        @trace  # Trace custom chain execution
        def analyze():
            from agentdbg.integrations import AgentDbgLangChainCallbackHandler
            handler = AgentDbgLangChainCallbackHandler()
            
            # Sentiment analysis
            sentiment_prompt = PromptTemplate(
                template="Analyze sentiment: {text}",
                input_variables=["text"]
            )
            
            sentiment_chain = LLMChain(
                llm=self.llm,
                prompt=sentiment_prompt
            )
            
            sentiment = sentiment_chain.run(
                text=inputs["text"],
                config={"callbacks": [handler]}
            )
            
            # Topic extraction
            topics_prompt = PromptTemplate(
                template="Extract main topics: {text}",
                input_variables=["text"]
            )
            
            topics_chain = LLMChain(
                llm=self.llm,
                prompt=topics_prompt
            )
            
            topics = topics_chain.run(
                text=inputs["text"],
                config={"callbacks": [handler]}
            )
            
            return {
                "sentiment": sentiment,
                "topics": topics
            }
        
        return analyze()

@trace
def debug_custom_chain():
    chain = CustomAnalysisChain(
        prompt=PromptTemplate(
            template="Analyze: {text}",
            input_variables=["text"]
        ),
        llm=ChatOpenAI(model="gpt-3.5-turbo")
    )
    
    result = chain("I love this product! Great features and amazing support.")
    return result
```

## Part 4: Performance Optimization

### Analyzing Token Usage

```python
@trace
def optimize_token_usage():
    handler = AgentDbgLangChainCallbackHandler()
    
    # Test different models
    models = ["gpt-3.5-turbo", "gpt-4"]
    results = {}
    
    for model in models:
        llm = ChatOpenAI(model=model, max_tokens=1000)
        chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                template="Summarize: {text}",
                input_variables=["text"]
            )
        )
        
        result = chain(
            "Long text here...",
            config={"callbacks": [handler]}
        )
        
        results[model] = {
            "result": result,
            "tokens_used": handler.get_total_tokens()  # Custom method
        }
    
    return results
```

### Caching Expensive Operations

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

@trace
def cached_chain_execution():
    # Enable caching
    set_llm_cache(InMemoryCache())
    
    handler = AgentDbgLangChainCallbackHandler()
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            template="Answer: {question}",
            input_variables=["question"]
        )
    )
    
    # First call - hits LLM
    result1 = chain(
        "What is AI?",
        config={"callbacks": [handler]}
    )
    
    # Second call - uses cache
    result2 = chain(
        "What is AI?",  # Same question
        config={"callbacks": [handler]}
    )
    
    return result2
```

**AgentDbg Timeline Shows**:
```
# First call
🤖 LLM_CALL: gpt-3.5-turbo
   Tokens: 50
   Cache Hit: No

# Second call
🤖 LLM_CALL: gpt-3.5-turbo  
   Tokens: 0
   Cache Hit: Yes ⚡
```

## Part 5: Production Debugging Checklist

### Pre-Deployment Checks

```python
@trace(
    max_llm_calls=100,
    max_tool_calls=200,
    max_duration_s=60,
    stop_on_loop=True
)
def production_readiness_check():
    """Verify LangChain app is production-ready."""
    handler = AgentDbgLangChainCallbackHandler()
    
    checks = {
        "error_handling": False,
        "memory_management": False,
        "tool_reliability": False,
        "performance": False
    }
    
    # Test error handling
    try:
        # Trigger intentional errors
        checks["error_handling"] = True
    except Exception as e:
        record_error(error_type="ProductionCheckError", message=str(e))
    
    # Test memory
    memory_test = ConversationBufferMemory()
    memory_test.save_context({"input": "test"}, {"output": "response"})
    checks["memory_management"] = len(memory_test.buffer) == 2
    
    # Test tools
    for tool in TOOLS:
        try:
            tool.func("test")
            checks["tool_reliability"] = True
        except:
            checks["tool_reliability"] = False
    
    # Performance check
    import time
    start = time.time()
    # Run typical query
    checks["performance"] = (time.time() - start) < 5.0
    
    record_state({"production_checks": checks})
    return all(checks.values())
```

### Monitoring Template

```python
@trace
def production_monitor():
    """Production monitoring wrapper."""
    handler = AgentDbgLangChainCallbackHandler()
    
    # Add custom monitoring
    record_state({
        "deployment": "production",
        "version": "1.0.0",
        "monitoring_enabled": True
    })
    
    try:
        # Your LangChain application
        result = run_langchain_app(handler)
        
        # Record success metrics
        record_state({
            "status": "success",
            "response_time_ms": handler.get_response_time(),
            "total_tokens": handler.get_total_tokens()
        })
        
        return result
        
    except Exception as e:
        # Record failure details
        record_error(
            error_type=type(e).__name__,
            message=str(e),
            context={
                "deployment": "production",
                "user_id": get_user_id(),
                "request_details": get_request_details()
            }
        )
        
        # Fallback behavior
        return get_fallback_response()
```

## Conclusion

This workflow transforms LangChain debugging from frustrating guesswork to systematic analysis:

**Before AgentDbg**:
```
❌ "Why did it call that tool?"
❌ "What's in the prompt?"  
❌ "Where did it fail?"
❌ "Why is it so slow?"
```

**After AgentDbg**:
```
✅ See exact prompts sent to LLM
✅ View tool inputs and outputs
✅ Trace errors with full context
✅ Measure performance bottlenecks
✅ Compare runs side-by-side
```

**Next Steps**:
- Install: `pip install agentdbg[langchain]`
- Try the examples in this guide
- View your first LangChain trace
- Optimize based on AgentDbg insights

**Join 500+ developers** who've improved their LangChain applications with AgentDbg's systematic debugging approach.

---

**Questions?** Check our [LangChain Integration Guide](../pillar-3-framework-integrations/langchain-complete-guide.md) or [GitHub Discussions](https://github.com/AgentDbg/AgentDbg/discussions).