"""
Speaking Calculator Service
Implements voice-based math calculator using ASR → NLU → Math Eval → TTS pipeline
"""
import re
import ast
import operator
from typing import Dict, Any, Optional, Tuple
from huggingface_hub import InferenceClient
from app.core.config import settings

# Hugging Face configuration
HF_TOKEN = settings.HUGGINGFACE_TOKEN


class SpeakingCalculator:
    """
    Voice-activated math calculator for kids.
    Pipeline: Audio → ASR → Math Parser → Evaluator → TTS Response
    """
    
    def __init__(self):
        self.client = InferenceClient(token=HF_TOKEN)
        
        # Models
        self.asr_model = "openai/whisper-small"  # ASR: Speech to text
        self.nlu_model = "google/flan-t5-base"  # NLU: Normalize expressions
        
        # Supported operations (safe subset)
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        # Number word mappings
        self.number_words = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
            'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
            'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000'
        }
        
        # Operation word mappings
        self.operation_words = {
            # Addition
            'plus': '+', 'add': '+', 'added to': '+', 'and': '+',
            # Subtraction
            'minus': '-', 'subtract': '-', 'take away': '-', 'less': '-',
            # Multiplication (most variations first for proper matching)
            'multiplied by': '×', 'multiply by': '×', 'multiply': '×', 
            'times': '×', 'time': '×',  # 'time' for when speech recognition drops the 's'
            'by': '×',  # "twelve by seven"
            'of': '×',  # "half of ten"
            'x': '×',   # literal 'x'
            # Division
            'divided by': '÷', 'divide by': '÷', 'divide': '÷', 'over': '÷',
            # Exponents
            'to the power of': '**', 'power': '**', 'raised to': '**',
            'squared': '**2', 'cubed': '**3',
            # Parentheses
            'open bracket': '(', 'close bracket': ')', 
            'open parenthesis': '(', 'close parenthesis': ')', 
            'left paren': '(', 'right paren': ')'
        }
    
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Convert spoken audio to text using Whisper ASR.
        
        Args:
            audio_bytes: Audio file bytes (WAV, MP3, etc.)
            
        Returns:
            Transcribed text
        """
        try:
            import requests
            
            print(f"Transcribing audio... Size: {len(audio_bytes)} bytes")
            
            # Use Hugging Face Inference API directly
            API_URL = f"https://api-inference.huggingface.co/models/{self.asr_model}"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            
            response = requests.post(API_URL, headers=headers, data=audio_bytes, timeout=30)
            
            print(f"ASR Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"ASR Result: {result}")
                
                if isinstance(result, dict) and 'text' in result:
                    transcription = result['text'].strip()
                    print(f"Transcription: {transcription}")
                    return transcription
                elif isinstance(result, list) and len(result) > 0:
                    transcription = result[0].get('text', '').strip()
                    print(f"Transcription (list): {transcription}")
                    return transcription
                print(f"Unexpected result format: {result}")
                return ""
            elif response.status_code == 503:
                print(f"Model is loading, please try again in a moment")
                return ""
            else:
                print(f"ASR API Error: {response.status_code} - {response.text}")
                return ""
            
        except Exception as e:
            print(f"ASR Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def normalize_to_expression(self, text: str) -> str:
        """
        Convert natural language to math expression.
        
        Examples:
            "what is twelve times seven?" → "12 × 7"
            "twenty five plus three" → "25 + 3"
            "five squared" → "5 ** 2"
        
        Args:
            text: Natural language math question
            
        Returns:
            Mathematical expression string
        """
        text = text.lower().strip()
        print(f"[NLU] Original text: '{text}'")
        
        # Remove question words
        text = re.sub(r'\b(what is|what\'s|calculate|compute|solve)\b', '', text)
        text = re.sub(r'\?', '', text)
        text = text.strip()
        print(f"[NLU] After removing question words: '{text}'")
        
        # Replace operation words with symbols (order matters - longer phrases first)
        # Sort by length descending to match longer phrases first
        sorted_ops = sorted(self.operation_words.items(), key=lambda x: len(x[0]), reverse=True)
        for word, symbol in sorted_ops:
            if word in text:
                text = text.replace(word, f' {symbol} ')
                print(f"[NLU] Replaced '{word}' with '{symbol}': '{text}'")
        
        # Replace number words with digits
        for word, digit in self.number_words.items():
            # Use word boundaries to avoid partial matches
            pattern = rf'\b{word}\b'
            if re.search(pattern, text):
                text = re.sub(pattern, digit, text)
                print(f"[NLU] Replaced number '{word}' with '{digit}': '{text}'")
        
        # Handle compound numbers (e.g., "twenty five" → "25")
        text = self._combine_number_words(text)
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert × and ÷ to Python operators
        text = text.replace('×', '*').replace('÷', '/')
        
        # Also handle any remaining 'x' that might mean multiply
        # Pattern: number x number (with word boundaries)
        text = re.sub(r'(\d+)\s+x\s+(\d+)', r'\1 * \2', text)
        
        print(f"[NLU] Final expression: '{text}'")
        return text
    
    def _combine_number_words(self, text: str) -> str:
        """Handle compound numbers like 'twenty five' → '25'"""
        # Pattern: tens + ones (e.g., 20 5 → 25)
        text = re.sub(r'(\d0)\s+(\d)\b', lambda m: str(int(m.group(1)) + int(m.group(2))), text)
        
        # Pattern: number + hundred (e.g., 5 100 → 500)
        text = re.sub(r'(\d+)\s+100', lambda m: str(int(m.group(1)) * 100), text)
        
        return text
    
    def safe_eval(self, expression: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Safely evaluate mathematical expression using AST.
        
        Args:
            expression: Math expression string (e.g., "12 * 7 + 5")
            
        Returns:
            Tuple of (result, error_message)
        """
        try:
            # Parse expression into AST
            node = ast.parse(expression, mode='eval')
            
            # Evaluate using safe eval
            result = self._eval_node(node.body)
            
            # Round to reasonable precision
            if isinstance(result, float):
                result = round(result, 6)
                # Remove trailing zeros
                if result == int(result):
                    result = int(result)
            
            return result, None
            
        except ZeroDivisionError:
            return None, "Cannot divide by zero"
        except SyntaxError:
            return None, "Invalid math expression"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def _eval_node(self, node):
        """Recursively evaluate AST node (safe evaluation)"""
        if isinstance(node, ast.Num):  # Number
            return node.n
        elif isinstance(node, ast.BinOp):  # Binary operation
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            
            if op_type not in self.operators:
                raise ValueError(f"Unsupported operation: {op_type}")
            
            return self.operators[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):  # Unary operation (e.g., -5)
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            
            if op_type not in self.operators:
                raise ValueError(f"Unsupported operation: {op_type}")
            
            return self.operators[op_type](operand)
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")
    
    def generate_response_text(self, expression: str, result: Any, spoken_text: str = "") -> str:
        """
        Generate kid-friendly response text.
        
        Args:
            expression: The math expression
            result: The calculated result
            spoken_text: Original spoken text (optional)
            
        Returns:
            Formatted response text for TTS
        """
        # Convert symbols back to words for speech
        expression_spoken = expression.replace('*', 'times').replace('/', 'divided by')
        expression_spoken = expression_spoken.replace('+', 'plus').replace('-', 'minus')
        
        # Create friendly response
        response = f"{expression_spoken} equals {result}."
        
        # Add encouraging phrase for kids
        encouragements = [
            "Great job!",
            "Well done!",
            "Excellent!",
            "You've got it!",
            "Fantastic!",
        ]
        
        import random
        encouragement = random.choice(encouragements)
        
        return f"{response} {encouragement}"
    
    def process_voice_calculation(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Full pipeline: Audio → ASR → NLU → Eval → Response
        
        Args:
            audio_bytes: Audio file bytes
            
        Returns:
            Dict with transcription, expression, result, response_text
        """
        # Step 1: ASR - Convert speech to text
        transcription = self.transcribe_audio(audio_bytes)
        
        if not transcription:
            return {
                'success': False,
                'error': 'Could not understand audio. Please try again.',
                'transcription': '',
                'expression': '',
                'result': None,
                'response_text': ''
            }
        
        # Step 2: NLU - Normalize to math expression
        expression = self.normalize_to_expression(transcription)
        
        if not expression or not any(c.isdigit() for c in expression):
            return {
                'success': False,
                'error': 'Could not find a math problem in your question.',
                'transcription': transcription,
                'expression': expression,
                'result': None,
                'response_text': ''
            }
        
        # Step 3: Evaluate expression safely
        result, error = self.safe_eval(expression)
        
        if error:
            return {
                'success': False,
                'error': error,
                'transcription': transcription,
                'expression': expression,
                'result': None,
                'response_text': ''
            }
        
        # Step 4: Generate response text
        response_text = self.generate_response_text(expression, result, transcription)
        
        return {
            'success': True,
            'error': None,
            'transcription': transcription,
            'expression': expression,
            'result': result,
            'response_text': response_text
        }
    
    def process_text_calculation(self, text: str) -> Dict[str, Any]:
        """
        Process text-based calculation (without audio).
        Useful for testing and fallback.
        
        Args:
            text: Natural language math question
            
        Returns:
            Dict with expression, result, response_text
        """
        # Step 1: NLU - Normalize to math expression
        expression = self.normalize_to_expression(text)
        
        if not expression or not any(c.isdigit() for c in expression):
            return {
                'success': False,
                'error': 'Could not find a math problem in your question.',
                'transcription': text,
                'expression': expression,
                'result': None,
                'response_text': ''
            }
        
        # Step 2: Evaluate expression safely
        result, error = self.safe_eval(expression)
        
        if error:
            return {
                'success': False,
                'error': error,
                'transcription': text,
                'expression': expression,
                'result': None,
                'response_text': ''
            }
        
        # Step 3: Generate response text
        response_text = self.generate_response_text(expression, result, text)
        
        return {
            'success': True,
            'error': None,
            'transcription': text,
            'expression': expression,
            'result': result,
            'response_text': response_text
        }


# Global instance
calculator_service = SpeakingCalculator()
