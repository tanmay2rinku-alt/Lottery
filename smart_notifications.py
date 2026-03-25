"""
Smart Notification Agent
Automated alerts for lottery results and predictions
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import time
from typing import List, Dict
from datetime import datetime


class SmartNotifier:
    """Smart notification system for lottery alerts"""
    
    def __init__(self, email_config: Dict = None, telegram_config: Dict = None):
        """
        Initialize notifier with email and/or Telegram config
        
        Args:
            email_config: {'smtp_server': str, 'smtp_port': int, 'username': str, 'password': str, 'from_email': str}
            telegram_config: {'bot_token': str, 'chat_id': str}
        """
        self.email_config = email_config
        self.telegram_config = telegram_config
        self.watchlist = []
        
        print("[NOTIFIER] Smart Notification Agent initialized")
    
    
    def add_to_watchlist(self, numbers: List[str]):
        """Add numbers to watchlist for alerts"""
        self.watchlist.extend([str(num) for num in numbers])
        self.watchlist = list(set(self.watchlist))  # Remove duplicates
        print(f"[NOTIFIER] Added {len(numbers)} numbers to watchlist. Total: {len(self.watchlist)}")
    
    
    def check_results_and_notify(self, winning_numbers: List[str], draw_time: str = "Unknown"):
        """Check if any watchlist numbers won and send notifications"""
        print(f"[NOTIFIER] Checking {len(winning_numbers)} results against {len(self.watchlist)} watchlist numbers...")
        
        matches = []
        for num in winning_numbers:
            if str(num) in self.watchlist:
                matches.append(str(num))
        
        if matches:
            print(f"[NOTIFIER] 🎉 MATCH FOUND! {len(matches)} watchlist numbers won: {matches}")
            self._send_match_alert(matches, draw_time)
        else:
            print("[NOTIFIER] No watchlist matches found")
    
    
    def _send_match_alert(self, matches: List[str], draw_time: str):
        """Send alert for winning watchlist numbers"""
        subject = f"🎉 LOTTERY MATCH ALERT - {draw_time} Draw!"
        message = f"""
🚨 LOTTERY WINNING ALERT 🚨

Congratulations! Your watchlist numbers have WON!

🎯 MATCHING NUMBERS: {', '.join(matches)}
⏰ DRAW TIME: {draw_time}
📅 DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Your lottery intelligence system detected these wins automatically.

Keep playing smart! 🍀
"""
        
        # Send email if configured
        if self.email_config:
            self._send_email_alert(subject, message)
        
        # Send Telegram if configured
        if self.telegram_config:
            self._send_telegram_alert(message)
    
    
    def _send_email_alert(self, subject: str, message: str):
        """Send email notification"""
        try:
            if not self.email_config:
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['from_email']  # Send to self for now
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], self.email_config['from_email'], text)
            server.quit()
            
            print("[NOTIFIER] 📧 Email alert sent successfully")
            
        except Exception as e:
            print(f"[NOTIFIER] ❌ Email alert failed: {str(e)}")
    
    
    def _send_telegram_alert(self, message: str):
        """Send Telegram notification"""
        try:
            if not self.telegram_config:
                return
            
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            
            payload = {
                'chat_id': self.telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("[NOTIFIER] 📱 Telegram alert sent successfully")
            else:
                print(f"[NOTIFIER] ❌ Telegram alert failed: {response.text}")
                
        except Exception as e:
            print(f"[NOTIFIER] ❌ Telegram alert failed: {str(e)}")
    
    
    def send_prediction_alert(self, top_picks: List[str], draw_time: str):
        """Send daily prediction recommendations"""
        subject = f"🎯 Daily Lottery Predictions - {draw_time} Draw"
        message = f"""
🎲 LOTTERY INTELLIGENCE PREDICTIONS 🎲

Your AI-powered lottery analysis has generated today's top picks!

🎯 TOP 5 RECOMMENDATIONS for {draw_time} Draw:
{chr(10).join([f'{i+1}. {num}' for i, num in enumerate(top_picks[:5])])}

📊 Analysis based on:
• Frequency patterns
• Statistical positioning  
• Recency analysis
• Series clustering
• Digit pattern matching

⏰ Draw Time: {draw_time}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Remember: Play responsibly! 🍀
"""
        
        # Send notifications
        if self.email_config:
            self._send_email_alert(subject, message)
        
        if self.telegram_config:
            self._send_telegram_alert(message)
        
        print(f"[NOTIFIER] 📤 Prediction alert sent for {draw_time} draw")


# Example usage and configuration
if __name__ == "__main__":
    # Example email config (Gmail)
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password',  # Use app password, not regular password
        'from_email': 'your_email@gmail.com'
    }
    
    # Example Telegram config
    telegram_config = {
        'bot_token': 'your_bot_token_here',
        'chat_id': 'your_chat_id_here'
    }
    
    # Initialize notifier
    notifier = SmartNotifier(email_config=email_config, telegram_config=telegram_config)
    
    # Add numbers to watchlist
    notifier.add_to_watchlist(['12345', '67890', '54321'])
    
    # Example: Check results
    winning_numbers = ['12345', '99999', '11111']
    notifier.check_results_and_notify(winning_numbers, "6PM")
    
    # Example: Send predictions
    top_picks = ['88990', '43444', '45678', '56789', '67890']
    notifier.send_prediction_alert(top_picks, "8PM")