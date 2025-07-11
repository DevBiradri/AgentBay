import os
import logging
import asyncio
import json
from enum import Enum
import speech_recognition as sr
import pyaudio
from dotenv import load_dotenv

# Google ADK imports
from google.adk.agents import Agent
from google.adk.sessions import Session
import google.generativeai as genai

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class AgentType(Enum):
    """Available agent types for orchestration"""
    LISTING_AGENT = "listing_agent"
    PRICING_AGENT = "pricing_agent"
    INVENTORY_AGENT = "inventory_agent"

class VoiceAgentConfig:
    """Configuration for the voice agent"""
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.record_seconds = 5  # Maximum recording time
        
        # Speech recognition settings
        self.sr_language = "en-US"
        self.energy_threshold = 300
        self.pause_threshold = 0.8

def convert_speech_to_text(audio_file_path: str = None, use_microphone: bool = True) -> dict:
    """
    Convert speech to text using Google Speech Recognition API
    
    Args:
        audio_file_path: Path to audio file (optional)
        use_microphone: Whether to use microphone input
    
    Returns:
        dict: {'status': 'success', 'text': '...', 'confidence': 0.95} or error dict
    """
    try:
        recognizer = sr.Recognizer()
        
        # Configure recognizer settings
        recognizer.energy_threshold = 300
        recognizer.pause_threshold = 0.8
        recognizer.phrase_threshold = 0.3
        
        if use_microphone:
            # Use microphone input
            with sr.Microphone(sample_rate=16000, chunk_size=1024) as source:
                logger.info("Listening for speech... Speak now!")
                
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
        else:
            # Use audio file input
            if not audio_file_path or not os.path.exists(audio_file_path):
                return {
                    "status": "error",
                    "error_message": "Audio file not found or path not provided"
                }
            
            with sr.AudioFile(audio_file_path) as source:
                audio = recognizer.record(source)
        
        # Convert speech to text using Google Speech Recognition
        try:
            # Use Google's free speech recognition service
            text = recognizer.recognize_google(audio, language="en-US")            
            logger.info(f"Speech recognized: {text}")
            
            return {
                "status": "success",
                "text": text.strip(),
                "confidence": confidence,
                "method": "google_free"
            }
            
        except sr.UnknownValueError:
            return {
                "status": "error",
                "error_message": "Could not understand the audio"
            }
        except sr.RequestError as e:
            return {
                "status": "error",
                "error_message": f"Google Speech Recognition service error: {e}"
            }
    
    except Exception as e:
        logger.error(f"Error in speech to text conversion: {e}")
        return {
            "status": "error",
            "error_message": f"Speech recognition failed: {str(e)}"
        }

def analyze_user_intent(text: str) -> dict:
    """
    Analyze user intent to determine which agent to call
    
    Args:
        text: Transcribed speech text
    
    Returns:
        dict: Intent analysis with agent routing information
    """
    try:
        if not text:
            return {
                "status": "error",
                "error_message": "No text provided for intent analysis"
            }
        
        # Initialize Gemini model for intent analysis
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Analyze this user query and determine which agent should handle it and extract relevant parameters.
        
        User Query: "{text}"
        
        Available Agents:
        1. listing_agent - Creates product listings from images, generates titles/descriptions
        2. pricing_agent - Analyzes pricing, market research, price recommendations
        3. inventory_agent - Manages inventory, stock levels, product tracking
        
        Intent Keywords:
        - listing_agent: "create listing", "list item", "sell", "auction", "product description", "title", "analyze image"
        - pricing_agent: "price", "cost", "value", "worth", "market price", "how much"
        - inventory_agent: "inventory", "stock", "count", "manage", "track", "add to inventory"
        
        Return JSON:
        {{
            "agent_type": "listing_agent|pricing_agent|inventory_agent",
            "confidence": 0.0-1.0,
            "intent_summary": "brief description of user intent",
            "extracted_parameters": {{
                "image_path": "path if mentioned",
                "product_name": "product name if mentioned",
                "price_range": "price range if mentioned",
                "quantity": "quantity if mentioned",
                "additional_info": "any other relevant info"
            }},
            "suggested_action": "specific action to take"
        }}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        try:
            intent_data = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback intent analysis using keywords
            text_lower = text.lower()
            
            if any(keyword in text_lower for keyword in ["list", "sell", "auction", "create listing", "product description", "title", "image"]):
                agent_type = "listing_agent"
            elif any(keyword in text_lower for keyword in ["price", "cost", "value", "worth", "market", "how much"]):
                agent_type = "pricing_agent"
            elif any(keyword in text_lower for keyword in ["inventory", "stock", "count", "manage", "track"]):
                agent_type = "inventory_agent"
            else:
                agent_type = "listing_agent"  # Default
            
            intent_data = {
                "agent_type": agent_type,
                "confidence": 0.7,
                "intent_summary": f"User wants to {agent_type.replace('_', ' ')}",
                "extracted_parameters": {
                    "image_path": None,
                    "product_name": None,
                    "price_range": None,
                    "quantity": None,
                    "additional_info": text
                },
                "suggested_action": f"Route to {agent_type}"
            }
        
        logger.info(f"Intent analyzed: {intent_data['agent_type']} (confidence: {intent_data['confidence']:.2f})")
        
        return {
            "status": "success",
            "intent": intent_data
        }
        
    except Exception as e:
        logger.error(f"Error analyzing intent: {e}")
        return {
            "status": "error",
            "error_message": f"Intent analysis failed: {str(e)}"
        }

def route_to_agent(intent_data: dict) -> dict:
    """
    Route the request to the appropriate agent based on intent analysis
    
    Args:
        intent_data: Intent analysis results
    
    Returns:
        dict: Agent routing information and action plan
    """
    try:
        agent_type = intent_data.get("agent_type", "listing_agent")
        parameters = intent_data.get("extracted_parameters", {})
        
        # Prepare routing information
        routing_info = {
            "target_agent": agent_type,
            "action": intent_data.get("suggested_action", "process_request"),
            "parameters": parameters,
            "confidence": intent_data.get("confidence", 0.7),
            "intent_summary": intent_data.get("intent_summary", "Process user request")
        }
        
        # Agent-specific routing logic
        if agent_type == "listing_agent":
            routing_info["required_tools"] = ["analyze_product_image", "create_complete_listing"]
            routing_info["expected_inputs"] = ["image_path"]
            
        elif agent_type == "pricing_agent":
            routing_info["required_tools"] = ["suggest_pricing", "market_analysis"]
            routing_info["expected_inputs"] = ["product_info", "condition"]
            
        elif agent_type == "inventory_agent":
            routing_info["required_tools"] = ["manage_inventory", "track_stock"]
            routing_info["expected_inputs"] = ["product_id", "quantity"]
        
        logger.info(f"Routing to {agent_type}: {routing_info['action']}")
        
        return {
            "status": "success",
            "routing": routing_info
        }
        
    except Exception as e:
        logger.error(f"Error routing to agent: {e}")
        return {
            "status": "error",
            "error_message": f"Agent routing failed: {str(e)}"
        }

def execute_agent_call(routing_info: dict) -> dict:
    """
    Execute the call to the target agent
    
    Args:
        routing_info: Agent routing information
    
    Returns:
        dict: Agent execution results
    """
    try:
        target_agent = routing_info["target_agent"]
        action = routing_info["action"]
        parameters = routing_info["parameters"]
        
        # Simulate agent calls (replace with actual agent implementations)
        if target_agent == "listing_agent":
            # Call listing agent
            result = {
                "agent": "listing_agent",
                "action": action,
                "result": "Listing agent would process the request",
                "parameters_used": parameters,
                "next_steps": ["Provide image path", "Generate listing"]
            }
            
        elif target_agent == "pricing_agent":
            # Call pricing agent
            result = {
                "agent": "pricing_agent",
                "action": action,
                "result": "Pricing agent would analyze market data",
                "parameters_used": parameters,
                "next_steps": ["Analyze market trends", "Provide price recommendations"]
            }
            
        elif target_agent == "inventory_agent":
            # Call inventory agent
            result = {
                "agent": "inventory_agent",
                "action": action,
                "result": "Inventory agent would manage stock",
                "parameters_used": parameters,
                "next_steps": ["Update inventory", "Track stock levels"]
            }
        
        logger.info(f"Agent call executed: {target_agent}")
        
        return {
            "status": "success",
            "execution_result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing agent call: {e}")
        return {
            "status": "error",
            "error_message": f"Agent execution failed: {str(e)}"
        }

def process_voice_input(audio_file_path: str = None, use_microphone: bool = True) -> dict:
    """
    Complete voice processing pipeline: Speech-to-Text -> Intent Analysis -> Agent Routing
    
    Args:
        audio_file_path: Path to audio file (optional)
        use_microphone: Whether to use microphone input
    
    Returns:
        dict: Complete processing results
    """
    try:
        logger.info("Starting voice input processing...")
        
        # Step 1: Convert speech to text
        speech_result = convert_speech_to_text(audio_file_path, use_microphone)
        if speech_result["status"] != "success":
            return speech_result
        
        text = speech_result["text"]
        logger.info(f"Speech converted to text: {text}")
        
        # Step 2: Analyze user intent
        intent_result = analyze_user_intent(text)
        if intent_result["status"] != "success":
            return intent_result
        
        intent_data = intent_result["intent"]
        logger.info(f"Intent analyzed: {intent_data['agent_type']}")
        
        # Step 3: Route to appropriate agent
        routing_result = route_to_agent(intent_data)
        if routing_result["status"] != "success":
            return routing_result
        
        routing_info = routing_result["routing"]
        logger.info(f"Routing to: {routing_info['target_agent']}")
        
        # Step 4: Execute agent call
        execution_result = execute_agent_call(routing_info)
        if execution_result["status"] != "success":
            return execution_result
        
        # Return complete pipeline results
        return {
            "status": "success",
            "pipeline_results": {
                "original_text": text,
                "speech_confidence": speech_result["confidence"],
                "intent_analysis": intent_data,
                "routing_info": routing_info,
                "agent_execution": execution_result["execution_result"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in voice processing pipeline: {e}")
        return {
            "status": "error",
            "error_message": f"Voice processing failed: {str(e)}"
        }

# Create the voice agent using Google ADK
root_agent = voice_agent = Agent(
    name="voice_agent",
    model="gemini-2.0-flash",
    description="AI voice agent that converts speech to text and orchestrates calls to other agents",
    instruction="""
    I am a voice-activated AI agent that processes spoken commands and routes them to appropriate specialized agents.
    
    My capabilities:
    - Convert speech to text using Google Speech Recognition
    - Analyze user intent from spoken commands
    - Route requests to the appropriate agent (listing, pricing, or inventory)
    - Execute agent calls based on the analyzed intent
    
    I can process both microphone input and audio files, and I'll determine which agent should handle your request based on what you say.
    
    Available agents I can route to:
    - Listing Agent: For creating product listings, analyzing images, generating descriptions
    - Pricing Agent: For price analysis, market research, valuation
    - Inventory Agent: For inventory management, stock tracking, product management
    
    Just speak your command and I'll take care of the rest!
    """,
    tools=[
        convert_speech_to_text,
        analyze_user_intent,
        route_to_agent,
        execute_agent_call,
        process_voice_input
    ]
)

class VoiceAgentOrchestrator:
    """
    Orchestrator for managing the voice agent and its interactions
    """
    
    def __init__(self):
        self.voice_agent = voice_agent
        self.config = VoiceAgentConfig()
        self.session = None
        
    def initialize_session(self):
        """Initialize a new session for the voice agent"""
        try:
            self.session = Session(agent=self.voice_agent)
            logger.info("Voice agent session initialized")
            return self.session
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return None
    
    async def process_voice_command(self, audio_file_path: str = None, use_microphone: bool = True):
        """
        Process a voice command through the complete pipeline
        """
        try:
            if not self.session:
                self.initialize_session()
            
            # Process the voice input
            result = process_voice_input(audio_file_path, use_microphone)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def start_continuous_listening(self):
        """
        Start continuous listening mode for voice commands
        """
        try:
            logger.info("Starting continuous voice listening mode...")
            logger.info("Say 'stop listening' to exit")
            
            while True:
                try:
                    # Process voice input
                    result = process_voice_input(use_microphone=True)
                    
                    if result["status"] == "success":
                        pipeline_results = result["pipeline_results"]
                        original_text = pipeline_results["original_text"]
                        
                        # Check for exit command
                        if "stop listening" in original_text.lower():
                            logger.info("Stopping continuous listening...")
                            break
                        
                        # Display results
                        print(f"\n--- Voice Command Processed ---")
                        print(f"You said: {original_text}")
                        print(f"Intent: {pipeline_results['intent_analysis']['intent_summary']}")
                        print(f"Routed to: {pipeline_results['routing_info']['target_agent']}")
                        print(f"Action: {pipeline_results['agent_execution']['action']}")
                        print(f"Result: {pipeline_results['agent_execution']['result']}")
                        print("---")
                        
                    else:
                        logger.error(f"Voice processing failed: {result['error_message']}")
                        
                except KeyboardInterrupt:
                    logger.info("Stopping continuous listening...")
                    break
                except Exception as e:
                    logger.error(f"Error in continuous listening: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error starting continuous listening: {e}")

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the voice agent orchestrator
        orchestrator = VoiceAgentOrchestrator()
        print("✓ Voice Agent initialized successfully!")
        
        # Test single voice command
        print("\n=== Testing Single Voice Command ===")
        result = asyncio.run(orchestrator.process_voice_command(use_microphone=True))
        
        if result["status"] == "success":
            print("Voice command processed successfully!")
            print(json.dumps(result["pipeline_results"], indent=2))
        else:
            print(f"Error: {result['error_message']}")
        
        # Uncomment to start continuous listening
        # print("\n=== Starting Continuous Listening ===")
        # orchestrator.start_continuous_listening()
        
    except Exception as e:
        print(f"Initialization error: {e}")
        logger.error(f"Initialization error: {e}")