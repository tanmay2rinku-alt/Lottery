"""
One-Click Executive Dashboard
Streamlit web UI for lottery intelligence visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
from typing import Dict, List

# Import our lottery modules
try:
    from lottery_analyzer import LotteryAnalyzer
    from number_scorer import SpecificNumberAnalyzer
    from sentiment_scraper import SentimentScraper
    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False


class LotteryDashboard:
    """Streamlit dashboard for lottery intelligence"""
    
    def __init__(self):
        self.db_path = "lottery_intelligence.db"
        st.set_page_config(
            page_title="Lottery Intelligence Dashboard",
            page_icon="🎯",
            layout="wide"
        )
    
    
    def run_dashboard(self):
        """Main dashboard application"""
        st.title("🎯 Lottery Intelligence Dashboard")
        st.markdown("---")
        
        # Sidebar
        self._create_sidebar()
        
        # Main content
        if not HAS_MODULES:
            st.error("⚠️ Lottery analysis modules not found. Please run the main system first.")
            return
        
        # Load data
        data = self._load_data()
        
        if not data:
            st.warning("📊 No lottery data available. Please run the main system to collect data.")
            return
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview", 
            "🎯 Predictions", 
            "📈 Analytics", 
            "🔍 Number Checker"
        ])
        
        with tab1:
            self._overview_tab(data)
        
        with tab2:
            self._predictions_tab(data)
        
        with tab3:
            self._analytics_tab(data)
        
        with tab4:
            self._number_checker_tab()
    
    
    def _create_sidebar(self):
        """Create sidebar with controls"""
        st.sidebar.title("🎲 Controls")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Quick Actions")
        
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.sidebar.button("📱 Send Predictions", use_container_width=True):
            self._send_predictions_notification()
            st.success("📤 Predictions sent!")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Settings")
        
        # Draw time selector
        draw_times = ["1PM", "6PM", "8PM", "All"]
        self.selected_draw = st.sidebar.selectbox(
            "Draw Time Filter",
            draw_times,
            index=3
        )
        
        # Number of predictions to show
        self.num_predictions = st.sidebar.slider(
            "Predictions to Show",
            min_value=5,
            max_value=20,
            value=10
        )
    
    
    def _load_data(self) -> Dict:
        """Load lottery data from database or generate sample"""
        try:
            if os.path.exists(self.db_path):
                return self._load_from_database()
            else:
                return self._generate_sample_data()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return {}
    
    
    def _load_from_database(self) -> Dict:
        """Load data from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        
        # Load winning numbers
        df = pd.read_sql_query("SELECT * FROM winning_numbers ORDER BY draw_date DESC", conn)
        
        # Load analysis results
        analysis_df = pd.read_sql_query("SELECT * FROM analysis_results ORDER BY created_at DESC LIMIT 1", conn)
        
        conn.close()
        
        return {
            'winning_numbers': df,
            'analysis': analysis_df.to_dict('records')[0] if not analysis_df.empty else {},
            'total_draws': len(df),
            'last_update': df['draw_date'].max() if not df.empty else None
        }
    
    
    def _generate_sample_data(self) -> Dict:
        """Generate sample data for demonstration"""
        # Sample winning numbers
        sample_numbers = [
            12345, 67890, 23456, 34567, 45678, 56789, 78901, 89012,
            90123, 11223, 22334, 33445, 44556, 55667, 66778, 77889,
            88990, 99001, 10111, 21222, 32333, 43444, 54555, 65666,
            76777, 87888, 98999
        ]
        
        # Create sample analysis
        analyzer = LotteryAnalyzer(sample_numbers)
        analysis = analyzer.analyze_all()
        
        return {
            'winning_numbers': sample_numbers,
            'analysis': analysis,
            'total_draws': len(sample_numbers),
            'last_update': datetime.now().strftime('%Y-%m-%d')
        }
    
    
    def _overview_tab(self, data: Dict):
        """Overview dashboard tab"""
        st.header("📊 Dashboard Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Draws", data.get('total_draws', 0))
        
        with col2:
            last_update = data.get('last_update', 'Never')
            st.metric("Last Update", str(last_update))
        
        with col3:
            analysis = data.get('analysis', {})
            total_series = analysis.get('series_analysis', {}).get('total_series', 0)
            st.metric("Series Found", total_series)
        
        with col4:
            prob_scores = analysis.get('probability_scores', {})
            top_score = max(prob_scores.values()) if prob_scores else 0
            st.metric("Top Probability", f"{top_score:.1f}%")
        
        st.markdown("---")
        
        # Recent winning numbers
        st.subheader("🏆 Recent Winning Numbers")
        winning_numbers = data.get('winning_numbers', [])
        
        if isinstance(winning_numbers, list):
            # Display as grid
            cols = st.columns(5)
            for i, num in enumerate(winning_numbers[-20:]):  # Last 20
                with cols[i % 5]:
                    st.code(f"{num:05d}", language="")
        else:
            # DataFrame format
            st.dataframe(winning_numbers.head(20))
    
    
    def _predictions_tab(self, data: Dict):
        """Predictions tab"""
        st.header("🎯 Today's Predictions")
        
        analysis = data.get('analysis', {})
        prob_scores = analysis.get('probability_scores', {})
        
        if not prob_scores:
            st.warning("No prediction data available")
            return
        
        # Top predictions
        top_predictions = sorted(prob_scores.items(), key=lambda x: x[1], reverse=True)[:self.num_predictions]
        
        st.subheader(f"Top {len(top_predictions)} Recommendations")
        
        # Display predictions in a nice format
        cols = st.columns(2)
        
        for i, (num, score) in enumerate(top_predictions):
            with cols[i % 2]:
                # Color based on score
                if score >= 70:
                    color = "🟢"
                    tier = "EXCELLENT"
                elif score >= 50:
                    color = "🟡"
                    tier = "GOOD"
                else:
                    color = "🔴"
                    tier = "MODERATE"
                
                st.markdown(f"""
                <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; margin: 5px;">
                    <h3 style="color: {color}; margin: 0;">{num:05d}</h3>
                    <p style="margin: 5px 0;">Probability: {score:.1f}%</p>
                    <p style="margin: 5px 0; font-weight: bold;">{tier}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Prediction chart
        st.subheader("📈 Prediction Distribution")
        
        df = pd.DataFrame(top_predictions, columns=['Number', 'Probability'])
        fig = px.bar(df, x='Number', y='Probability',
                    title=f'Top {len(top_predictions)} Lottery Predictions',
                    color='Probability',
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    
    def _analytics_tab(self, data: Dict):
        """Analytics tab"""
        st.header("📈 Advanced Analytics")
        
        analysis = data.get('analysis', {})
        
        # Series analysis
        if 'series_analysis' in analysis:
            st.subheader("🎭 Series Analysis (First 2 Digits)")
            
            series_data = analysis['series_analysis']['series_distribution']
            series_df = pd.DataFrame.from_dict(series_data, orient='index')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Series frequency chart
                fig = px.pie(series_df, values='count', names=series_df.index,
                           title='Series Distribution')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Series statistics
                st.dataframe(series_df[['count', 'frequency']].sort_values('count', ascending=False))
        
        # Recency analysis
        if 'recency_analysis' in analysis:
            st.subheader("⏰ Recency Analysis")
            
            recency = analysis['recency_analysis']
            overdue = recency.get('overdue_numbers', [])
            
            if overdue:
                st.write("**Most Overdue Numbers (Statistically Due):**")
                for num, score in overdue[:5]:
                    st.write(f"• {num:05d} (Recency: {score:.1f}%)")
        
        # Sentiment analysis (if available)
        st.subheader("📺 Social Sentiment")
        try:
            scraper = SentimentScraper()
            sentiment_data = scraper.scrape_youtube_predictions(max_videos=3)
            
            if 'error' not in sentiment_data:
                sentiment = sentiment_data.get('sentiment_summary', {})
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Sentiment", sentiment.get('sentiment', 'neutral').upper())
                
                with col2:
                    st.metric("Confidence", f"{sentiment.get('confidence', 0):.1f}%")
                
                with col3:
                    st.metric("Videos", sentiment_data.get('videos_analyzed', 0))
                
                # Trending numbers
                if sentiment_data.get('trending_numbers'):
                    st.write("**Trending Numbers from YouTube:**")
                    for num, freq in sentiment_data['trending_numbers'][:3]:
                        st.write(f"• {num} (mentioned {freq} times)")
            else:
                st.info("Unable to fetch YouTube sentiment data")
                
        except Exception as e:
            st.info("Sentiment analysis unavailable")
    
    
    def _number_checker_tab(self):
        """Number checker tab"""
        st.header("🔍 Number Probability Checker")
        
        # Input
        number_input = st.text_input(
            "Enter a 5-digit lottery number:",
            placeholder="12345",
            max_chars=5
        )
        
        if st.button("🔍 Analyze Number", type="primary"):
            if len(number_input) == 5 and number_input.isdigit():
                self._analyze_specific_number(int(number_input))
            else:
                st.error("Please enter a valid 5-digit number")
    
    
    def _analyze_specific_number(self, number: int):
        """Analyze a specific number"""
        try:
            # Load historical data
            data = self._load_data()
            winning_numbers = data.get('winning_numbers', [])
            
            if isinstance(winning_numbers, list):
                analyzer = SpecificNumberAnalyzer(winning_numbers)
                analysis = analyzer.analyze_number(number)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    score = analysis['total_score']
                    if score >= 70:
                        st.success(f"Score: {score:.1f}%")
                        st.write("**EXCELLENT**")
                    elif score >= 50:
                        st.warning(f"Score: {score:.1f}%")
                        st.write("**GOOD**")
                    else:
                        st.error(f"Score: {score:.1f}%")
                        st.write("**MODERATE**")
                
                with col2:
                    st.metric("Frequency", analysis.get('appeared_count', 0))
                
                with col3:
                    st.metric("Digit Sum", analysis.get('digit_sum', 0))
                
                # Factor breakdown
                st.subheader("📊 Factor Breakdown")
                
                factors = analysis.get('score_breakdown', {})
                factor_df = pd.DataFrame([
                    {
                        'Factor': k.replace('_', ' ').title(),
                        'Score': f"{v['score']:.1f}%",
                        'Weight': f"{v['weight']*100:.0f}%",
                        'Contribution': f"{v['weighted_contribution']:.1f}%"
                    }
                    for k, v in factors.items()
                ])
                
                st.dataframe(factor_df, use_container_width=True)
                
                # Recommendations
                st.subheader("💡 Recommendations")
                tier = "EXCELLENT" if score >= 70 else "GOOD" if score >= 50 else "MODERATE"
                st.write(f"This number is in the **{tier}** tier.")
                
                if score >= 70:
                    st.success("🎯 Strong recommendation to play this number!")
                elif score >= 50:
                    st.info("👍 Consider playing this number.")
                else:
                    st.warning("🤔 This number has below-average probability.")
                
            else:
                st.error("Unable to load historical data for analysis")
                
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
    
    
    def _send_predictions_notification(self):
        """Send predictions via notification system"""
        try:
            from smart_notifications import SmartNotifier
            
            # Load data
            data = self._load_data()
            analysis = data.get('analysis', {})
            prob_scores = analysis.get('probability_scores', {})
            
            if prob_scores:
                top_5 = [str(num) for num, score in 
                        sorted(prob_scores.items(), key=lambda x: x[1], reverse=True)[:5]]
                
                # Initialize notifier (you would configure this with real credentials)
                notifier = SmartNotifier()
                notifier.send_prediction_alert(top_5, "6PM")
                
        except ImportError:
            st.warning("Notification system not configured")
        except Exception as e:
            st.warning(f"Could not send notifications: {str(e)}")


def main():
    """Run the dashboard"""
    dashboard = LotteryDashboard()
    dashboard.run_dashboard()


if __name__ == "__main__":
    main()