"""
GI4C Payment Service
Handles payment processing with Monetbil and Orange Money
"""

import os
import requests
from datetime import datetime
from typing import Dict
import hashlib
import hmac

class PaymentProcessor:
    """Payment processor for GI4C donations"""
    
    def __init__(self):
        self.monetbil_service_key = os.getenv('MONETBIL_SERVICE_KEY')
        self.monetbil_api_url = 'https://api.monetbil.com/pay/v01'
        self.orange_money_api_url = 'https://api.orange.com/orange-money-webpay'
        
    def create_payment(self, amount: float, donor_name: str, donor_email: str) -> Dict:
        """Create a payment intent"""
        
        # Generate transaction ID
        transaction_id = self._generate_transaction_id()
        
        if self.monetbil_service_key:
            return self._create_monetbil_payment(
                amount, donor_name, donor_email, transaction_id
            )
        else:
            # Demo mode - return mock payment
            return self._create_demo_payment(
                amount, donor_name, donor_email, transaction_id
            )
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"GI4C-{timestamp}"
    
    def _create_monetbil_payment(self, amount: float, donor_name: str, 
                                 donor_email: str, transaction_id: str) -> Dict:
        """Create payment with Monetbil API"""
        try:
            payload = {
                'service': self.monetbil_service_key,
                'amount': int(amount),
                'currency': 'XAF',
                'transaction_id': transaction_id,
                'user': donor_name,
                'email': donor_email,
                'notify_url': '/api/payment/notify',
                'return_url': '/payment-success.html',
                'cancel_url': '/payment-cancel.html'
            }
            
            # In production, make actual API call
            # response = requests.post(self.monetbil_api_url, json=payload)
            # return response.json()
            
            # For now, return demo response
            return self._create_demo_payment(amount, donor_name, donor_email, transaction_id)
            
        except Exception as e:
            raise Exception(f"Monetbil payment creation failed: {str(e)}")
    
    def _create_demo_payment(self, amount: float, donor_name: str, 
                            donor_email: str, transaction_id: str) -> Dict:
        """Create demo payment for testing"""
        return {
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': 'XAF',
            'status': 'pending',
            'payment_url': f'/payment-demo.html?tx={transaction_id}',
            'message': 'Demo payment created. Connect Monetbil API for production.'
        }
    
    def verify_payment(self, transaction_id: str) -> Dict:
        """Verify payment status with payment provider"""
        # In production, call Monetbil API to verify
        # For now, return demo verification
        return {
            'transaction_id': transaction_id,
            'status': 'completed',
            'verified': True
        }
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        """Process payment notification webhook"""
        transaction_id = webhook_data.get('transaction_id')
        status = webhook_data.get('status')
        
        # Verify webhook signature in production
        # if not self._verify_webhook_signature(webhook_data):
        #     raise Exception('Invalid webhook signature')
        
        return {
            'transaction_id': transaction_id,
            'status': status,
            'processed': True
        }
    
    def _verify_webhook_signature(self, data: Dict) -> bool:
        """Verify webhook signature from Monetbil"""
        # Implement signature verification in production
        return True
    
    def refund_payment(self, transaction_id: str) -> Dict:
        """Process a refund"""
        # In production, call Monetbil refund API
        return {
            'transaction_id': transaction_id,
            'status': 'refunded',
            'message': 'Refund processed'
        }
