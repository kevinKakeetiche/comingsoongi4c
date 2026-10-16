"""
GI4C AI Assistant Service
Handles AI/ML integration for the assistant
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import json

# Try to import OpenAI, fallback to demo mode if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIAssistant:
    """AI Assistant for GI4C knowledge support"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Knowledge base (can be extended with RAG)
        self.knowledge_base = self._load_knowledge_base()
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def _load_knowledge_base(self) -> Dict:
        """Load GI4C knowledge base"""
        return {
            'programs': {
                'emergency_response': 'Rapid deployment of information management teams during declared emergencies.',
                'data_analytics': 'Dashboards, GIS mapping and models that turn field reports into actionable insight.',
                'local_capacity': 'Training and systems that strengthen local teams and institutions.',
                'community_resilience': 'Community-led approaches that support resilience, livelihoods and inclusion.'
            },
            'mission': 'GI4C exists to leverage technology, data, and localized research to strengthen public systems and empower communities by translating real-time intelligence into informed decisions and coordinated action that advance healthy people, resilient systems, and sustainable communities.',
            'values': ['Community-Centred', 'Integrity', 'Responsibility', 'Collaboration', 'Learning & Evidence', 'Equity & Inclusion'],
            'contact': {
                'email': 'info@gi4c.org',
                'location': 'Yaoundé, Cameroon',
                'website': 'www.gi4c.org'
            },
            'initiatives': {
                'operation_20k_trees': 'A community-based reforestation and agroforestry approach in Machatoum, Cameroon, targeting 20,000 trees from 2023-2028, with 2,300 trees planted.'
            }
        }
    
    def generate_response(self, user_message: str, session_id: str) -> Dict:
        """Generate AI response to user message"""
        
        if self.client and OPENAI_AVAILABLE:
            return self._generate_openai_response(user_message, session_id)
        else:
            return self._generate_demo_response(user_message)
    
    def _generate_openai_response(self, user_message: str, session_id: str) -> Dict:
        """Generate response using OpenAI API"""
        try:
            system_prompt = f"""You are a helpful assistant for GI4C (Global Impact for Communities), 
a non-profit organization focused on community data intelligence and systems strengthening.

Key information about GI4C:
- Mission: {self.knowledge_base['mission']}
- Values: {', '.join(self.knowledge_base['values'])}
- Contact: {self.knowledge_base['contact']['email']}, {self.knowledge_base['contact']['location']}

Programs:
- Emergency Response: {self.knowledge_base['programs']['emergency_response']}
- Data & Analytics: {self.knowledge_base['programs']['data_analytics']}
- Local Capacity: {self.knowledge_base['programs']['local_capacity']}
- Community Resilience: {self.knowledge_base['programs']['community_resilience']}

Current Initiative:
- Operation 20K Trees: {self.knowledge_base['initiatives']['operation_20k_trees']}

Provide helpful, accurate responses about GI4C's work. If you don't know something specific, 
suggest the user contact info@gi4c.org for more detailed information."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                'message': response.choices[0].message.content,
                'sources': ['GI4C Knowledge Base'],
                'metadata': {
                    'model': self.model,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return self._generate_demo_response(user_message)
    
    def _generate_demo_response(self, user_message: str) -> Dict:
        """Generate demo response without AI API"""
        message_lower = user_message.lower()
        
        # Simple keyword matching for demo
        if 'program' in message_lower or 'work' in message_lower:
            response = "GI4C has four main program areas:\n\n1. **Emergency Response** - Rapid deployment of information management teams during declared emergencies.\n2. **Data & Analytics** - Dashboards, GIS mapping and models that turn field reports into actionable insight.\n3. **Local Capacity** - Training and systems that strengthen local teams and institutions.\n4. **Community Resilience** - Community-led approaches that support resilience, livelihoods and inclusion.\n\nWould you like more details about any specific program?"
        
        elif 'mission' in message_lower or 'about' in message_lower or 'who' in message_lower:
            response = f"GI4C's mission is to make community needs, vulnerabilities, and opportunities visible through continuous community intelligence. We work with governments, communities, donors, and development partners to translate evidence into better decisions and coordinated interventions.\n\nOur values are: {', '.join(self.knowledge_base['values'])}."
        
        elif 'contact' in message_lower or 'email' in message_lower or 'reach' in message_lower:
            response = f"You can contact GI4C at:\n- Email: {self.knowledge_base['contact']['email']}\n- Location: {self.knowledge_base['contact']['location']}\n- Website: {self.knowledge_base['contact']['website']}"
        
        elif 'tree' in message_lower or 'reforest' in message_lower or 'environment' in message_lower:
            response = f"Operation 20K Trees is GI4C's current initiative in Machatoum, Cameroon. It's a community-based reforestation and agroforestry approach running from 2023-2028, with 2,300 of 20,000 target trees planted. A GIS/GPS-enabled tree registry will document planting locations, species, dates, survival and growth."
        
        elif 'donate' in message_lower or 'support' in message_lower or 'contribute' in message_lower:
            response = "Thank you for your interest in supporting GI4C! You can make donations through our Donate page, which supports Monetbil and Orange Money payments in FCFA (XAF). Your contribution helps fund our programs and initiatives like Operation 20K Trees."
        
        elif 'data' in message_lower or 'dashboard' in message_lower or 'analytics' in message_lower:
            response = "GI4C's data intelligence capabilities include:\n- Live dashboards for health, surveillance, and community data\n- GIS mapping for risk, vulnerability, and heat maps\n- Published reports including situation reports, policy briefs, and early warning bulletins\n- AI Assistant for knowledge support\n\nThe dashboard is ready to connect to verified GI4C programme data, GIS, and APIs."
        
        else:
            response = "I'm the GI4C AI Assistant. I can help you with information about our programs, mission, team, impact, initiatives like Operation 20K Trees, and how to get involved or donate. What would you like to know?"
        
        return {
            'message': response,
            'sources': ['GI4C Knowledge Base (Demo Mode)'],
            'metadata': {
                'mode': 'demo',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text (placeholder for ML integration)"""
        # This would use a proper ML model in production
        # For now, return a simple analysis
        text_lower = text.lower()
        
        positive_words = ['good', 'great', 'excellent', 'helpful', 'thanks', 'appreciate']
        negative_words = ['bad', 'poor', 'difficult', 'problem', 'issue', 'concern']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': 0.7,  # Placeholder
            'positive_score': positive_count,
            'negative_score': negative_count
        }
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (placeholder for NER)"""
        # This would use a proper NER model in production
        entities = []
        
        # Simple extraction based on knowledge base
        for program in self.knowledge_base['programs'].keys():
            if program.replace('_', ' ') in text.lower():
                entities.append(program)
        
        return entities
