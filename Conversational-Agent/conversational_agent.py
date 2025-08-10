import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ConversationalAgent:
    """Enhanced conversational agent that maintains context and provides intelligent responses."""
    
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """You are an intelligent AI assistant specialized in Neo4j graph databases and PDF document analysis. 
        
Your capabilities include:
1. Answering questions about Neo4j graph databases
2. Analyzing and explaining PDF documents
3. Generating Cypher queries for graph operations
4. Providing insights about uploaded documents
5. Helping users understand data relationships

You should:
- Maintain conversation context
- Provide helpful, accurate responses
- Ask clarifying questions when needed
- Suggest relevant queries or analyses
- Be conversational and engaging
- Use the conversation history to provide context-aware responses

Current conversation context: {context}

Available functions:
- Generate Cypher queries
- Analyze PDF content
- Search document content
- Explain graph relationships
- Provide data insights"""
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": "now"  # Could be enhanced with actual timestamps
        })
    
    def get_context_summary(self) -> str:
        """Generate a summary of the conversation context."""
        if len(self.conversation_history) <= 2:
            return "New conversation started."
        
        # Get last few messages for context
        recent_messages = self.conversation_history[-4:]
        context_parts = []
        
        for msg in recent_messages:
            if msg["role"] == "user":
                context_parts.append(f"User asked: {msg['content'][:100]}...")
            elif msg["role"] == "assistant":
                context_parts.append(f"Assistant responded: {msg['content'][:100]}...")
        
        return " | ".join(context_parts)
    
    def generate_response(self, user_input: str, pdf_context: str = None, graph_context: str = None) -> Dict[str, Any]:
        """
        Generate a contextual response based on user input and available context.
        
        Args:
            user_input: The user's message
            pdf_context: Information about uploaded PDFs
            graph_context: Information about the graph database
            
        Returns:
            Dictionary containing response type, content, and any additional data
        """
        # Add user message to history
        self.add_message("user", user_input)
        
        # Build context
        context_parts = [self.get_context_summary()]
        if pdf_context:
            context_parts.append(f"PDF Context: {pdf_context}")
        if graph_context:
            context_parts.append(f"Graph Context: {graph_context}")
        
        full_context = " | ".join(context_parts)
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": self.system_prompt.format(context=full_context)},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Add assistant response to history
            self.add_message("assistant", assistant_response)
            
            # Determine response type and additional actions
            response_data = {
                "type": "conversation",
                "content": assistant_response,
                "conversation_history": self.conversation_history[-6:],  # Last 6 messages
                "suggested_actions": self._suggest_actions(user_input, assistant_response)
            }
            
            return response_data
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}. Please try again."
            self.add_message("assistant", error_response)
            
            return {
                "type": "error",
                "content": error_response,
                "conversation_history": self.conversation_history[-6:],
                "suggested_actions": []
            }
    
    def _suggest_actions(self, user_input: str, response: str) -> List[str]:
        """Suggest relevant actions based on the conversation."""
        suggestions = []
        
        # Analyze user input and response to suggest actions
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        if any(word in input_lower for word in ["pdf", "document", "upload", "file"]):
            suggestions.append("Upload a PDF document for analysis")
            suggestions.append("Search existing PDF content")
            suggestions.append("View uploaded documents")
        
        if any(word in input_lower for word in ["query", "cypher", "graph", "database", "neo4j"]):
            suggestions.append("Generate a Cypher query")
            suggestions.append("Explore graph relationships")
            suggestions.append("Run a database query")
        
        if any(word in input_lower for word in ["analyze", "understand", "explain", "what"]):
            suggestions.append("Get detailed analysis")
            suggestions.append("Explore related data")
            suggestions.append("Generate insights report")
        
        # Add general suggestions
        if not suggestions:
            suggestions.append("Upload a PDF for analysis")
            suggestions.append("Ask about the graph database")
            suggestions.append("Generate a Cypher query")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the entire conversation."""
        if not self.conversation_history:
            return "No conversation history."
        
        summary_parts = []
        for i, msg in enumerate(self.conversation_history):
            role = "User" if msg["role"] == "user" else "Assistant"
            summary_parts.append(f"{i+1}. {role}: {msg['content'][:100]}...")
        
        return "\n".join(summary_parts) 