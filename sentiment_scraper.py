"""
Automated Sentiment/Trend Scraper
Scrapes YouTube lottery prediction videos for trending lucky numbers
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import json


class SentimentScraper:
    """Scraper for lottery prediction trends from YouTube"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print("[SCRAPER] Sentiment Trend Scraper initialized")
    
    
    def scrape_youtube_predictions(self, max_videos: int = 5) -> Dict:
        """Scrape top lottery prediction videos from YouTube"""
        print(f"[SCRAPER] Scraping top {max_videos} lottery prediction videos...")
        
        try:
            # YouTube search URL for lottery predictions
            search_query = "lottery prediction today lucky numbers"
            search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract video information (this is a simplified approach)
            # Note: YouTube's HTML structure changes frequently
            videos_data = []
            
            # Look for video links and titles
            video_elements = soup.find_all('a', {'href': re.compile(r'/watch\?v=')})
            
            for elem in video_elements[:max_videos]:
                video_id = elem.get('href', '').split('v=')[1].split('&')[0] if 'v=' in elem.get('href', '') else None
                title = elem.get('title', '') or elem.text.strip()
                
                if video_id and title:
                    videos_data.append({
                        'video_id': video_id,
                        'title': title,
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
            
            # Extract lucky numbers from titles
            all_numbers = []
            guru_predictions = {}
            
            for video in videos_data:
                title = video['title'].lower()
                
                # Extract 5-digit numbers from title
                numbers_in_title = re.findall(r'\b\d{5}\b', title)
                if numbers_in_title:
                    guru_predictions[video['title'][:50] + "..."] = numbers_in_title
                    all_numbers.extend(numbers_in_title)
            
            # Analyze trends
            number_frequency = {}
            for num in all_numbers:
                number_frequency[num] = number_frequency.get(num, 0) + 1
            
            trending_numbers = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'videos_analyzed': len(videos_data),
                'guru_predictions': guru_predictions,
                'trending_numbers': trending_numbers[:10],  # Top 10 trending
                'total_unique_numbers': len(set(all_numbers)),
                'sentiment_summary': self._analyze_sentiment(guru_predictions)
            }
            
            print(f"[SCRAPER] Found {len(videos_data)} videos with {len(set(all_numbers))} unique numbers")
            return results
            
        except Exception as e:
            print(f"[SCRAPER] Error scraping YouTube: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'videos_analyzed': 0
            }
    
    
    def _analyze_sentiment(self, guru_predictions: Dict) -> Dict:
        """Analyze sentiment from guru predictions"""
        if not guru_predictions:
            return {'sentiment': 'neutral', 'confidence': 0}
        
        # Simple sentiment analysis based on keywords
        positive_words = ['lucky', 'win', 'jackpot', 'guaranteed', 'sure', 'confirmed']
        negative_words = ['avoid', 'skip', 'bad', 'unlucky', 'danger']
        
        positive_count = 0
        negative_count = 0
        
        for title, numbers in guru_predictions.items():
            title_lower = title.lower()
            positive_count += sum(1 for word in positive_words if word in title_lower)
            negative_count += sum(1 for word in negative_words if word in title_lower)
        
        total_signals = positive_count + negative_count
        
        if total_signals == 0:
            sentiment = 'neutral'
            confidence = 50
        elif positive_count > negative_count:
            sentiment = 'bullish'
            confidence = min(100, (positive_count / total_signals) * 100)
        else:
            sentiment = 'bearish'
            confidence = min(100, (negative_count / total_signals) * 100)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_signals': positive_count,
            'negative_signals': negative_count
        }
    
    
    def compare_with_mathematical(self, guru_numbers: List[str], math_top_5: List[str]) -> Dict:
        """Compare guru predictions with mathematical analysis"""
        guru_set = set(guru_numbers)
        math_set = set(math_top_5)
        
        overlap = guru_set.intersection(math_set)
        guru_only = guru_set - math_set
        math_only = math_set - guru_set
        
        alignment_score = (len(overlap) / len(math_set)) * 100 if math_set else 0
        
        return {
            'alignment_score': alignment_score,
            'overlapping_numbers': list(overlap),
            'guru_only': list(guru_only),
            'math_only': list(math_only),
            'conclusion': self._generate_comparison_conclusion(alignment_score)
        }
    
    
    def _generate_comparison_conclusion(self, alignment_score: float) -> str:
        """Generate conclusion based on alignment score"""
        if alignment_score >= 80:
            return "Excellent alignment! Gurus and math agree strongly."
        elif alignment_score >= 60:
            return "Good alignment. Consider combining both approaches."
        elif alignment_score >= 40:
            return "Moderate alignment. Math may provide edge over gurus."
        elif alignment_score >= 20:
            return "Low alignment. Math analysis likely superior."
        else:
            return "Poor alignment. Stick to mathematical analysis."


# Example usage
if __name__ == "__main__":
    scraper = SentimentScraper()
    
    # Scrape YouTube predictions
    results = scraper.scrape_youtube_predictions(max_videos=5)
    
    print("\n" + "="*60)
    print("YOUTUBE LOTTERY PREDICTION ANALYSIS")
    print("="*60)
    
    if 'error' not in results:
        print(f"Videos Analyzed: {results['videos_analyzed']}")
        print(f"Unique Numbers Found: {results['total_unique_numbers']}")
        
        print("\n[GURU PREDICTIONS]")
        for title, numbers in results['guru_predictions'].items():
            print(f"  {title}: {numbers}")
        
        print("\n[TRENDING NUMBERS]")
        for num, freq in results['trending_numbers'][:5]:
            print(f"  {num}: mentioned {freq} times")
        
        sentiment = results['sentiment_summary']
        print(f"\n[SENTIMENT ANALYSIS]")
        print(f"  Overall Sentiment: {sentiment['sentiment'].upper()}")
        print(f"  Confidence: {sentiment['confidence']:.1f}%")
        
    else:
        print(f"Error: {results['error']}")
    
    # Example comparison with mathematical analysis
    math_top_5 = ['88990', '43444', '45678', '56789', '67890']
    guru_numbers = []
    for nums in results.get('guru_predictions', {}).values():
        guru_numbers.extend(nums)
    
    if guru_numbers:
        comparison = scraper.compare_with_mathematical(guru_numbers, math_top_5)
        print(f"\n[COMPARISON WITH MATH ANALYSIS]")
        print(f"  Alignment Score: {comparison['alignment_score']:.1f}%")
        print(f"  Overlapping: {comparison['overlapping_numbers']}")
        print(f"  Guru Only: {comparison['guru_only']}")
        print(f"  Math Only: {comparison['math_only']}")
        print(f"  Conclusion: {comparison['conclusion']}")