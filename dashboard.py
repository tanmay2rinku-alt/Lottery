"""
Pipeline 6: One-Click Executive Dashboard
Streamlit web UI for lottery intelligence visualization (Supabase Integrated)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import json
import os

from supabase_client import SupabaseClient
from university_math import UniversityMathEngine
from config import SUPABASE_URL, SUPABASE_KEY

class LotteryDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Lottery Intelligence Dashboard",
            page_icon="🎯",
            layout="wide"
        )
        self.db = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)
    
    def _fetch_supabase_data(self):
        try:
            winners = self.db.supabase.table('winning_numbers').select('*').order('draw_date', desc=True).limit(500).execute().data
            df_winners = pd.DataFrame(winners)
            analysis = self.db.supabase.table('analysis_results').select('*').order('created_at', desc=True).limit(5).execute().data
            
            analysis_map = {}
            for item in analysis:
                a_type = item['analysis_type']
                if a_type not in analysis_map:
                    res = item.get('results_json')
                    if isinstance(res, str):
                        try: res = json.loads(res)
                        except: pass
                    analysis_map[a_type] = res
            
            return {
                "winners": df_winners,
                "analysis": analysis_map,
                "last_update": df_winners['created_at'].iloc[0] if not df_winners.empty else "N/A"
            }
        except Exception as e:
            st.error(f"Failed to fetch data from Supabase: {e}")
            return None

    def run(self):
        st.title("🎯 Lottery Intelligence Executive Dashboard")
        st.markdown(f"*Nagaland Dear Lottery - 6-Pipeline Automation*")
        
        data = self._fetch_supabase_data()
        if not data: return

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "🎓 University Math", "🤝 Guru Consensus", "🔮 Smart Predictor"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Historical Records", len(data['winners']))
            with col2:
                st.metric("Last Draw Scraped", data['winners']['draw_date'].iloc[0] if not data['winners'].empty else "N/A")
            with col3:
                st.write("**Recent Winning Numbers**")
                if not data['winners'].empty:
                    st.dataframe(data['winners'][['number', 'draw_time', 'draw_date']].head(10))

        with tab2:
            st.header("🎓 University-Grade Math Analytics (MIT/Stanford)")
            math_data = data['analysis'].get('university_math')
            if math_data:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.subheader("Monte Carlo Simulation")
                    picks = math_data.get('monte_carlo', {}).get('top_simulated_picks', [])
                    st.success(f"Top 5 Projected: {', '.join(map(str, picks[:5]))}")
                with c2:
                    st.subheader("Poisson Arrival Rate")
                    p_data = math_data.get('poisson', {})
                    st.metric("Repeat Probability", f"{p_data.get('prob_of_repeat', 0)*100:.1f}%")
                with c3:
                    st.subheader("Chi-Squared Test")
                    chi = math_data.get('chi_squared', {})
                    st.info(chi.get('interpretation', 'Statistically Random'))
            else:
                st.warning("Run the Orchestrator to generate University Math data.")

        with tab3:
            st.header("🤝 Consensus: Gurus vs Mathematical Reality")
            sentiment = data['analysis'].get('sentiment_trends')
            if sentiment:
                consensus = sentiment.get('math_consensus', [])
                if consensus:
                    st.success(f"🔥 **CONSENSUS MATCH FOUND**: {', '.join(map(str, consensus))}")
                alignment = sentiment.get('comparison_with_math', {}).get('alignment_score', 0)
                st.progress(alignment / 100)
            else:
                st.warning("Run the Orchestrator to capture Sentiment Consensus.")

        with tab4:
            st.header("🔮 Smart Individual Predictor")
            st.markdown("Enter any number to analyze its probability against historical patterns.")
            
            input_num = st.number_input("Target Number", min_value=0, max_value=99999, value=12345)
            if st.button("Generate Intelligence Report"):
                if not data['winners'].empty:
                    engine = UniversityMathEngine(data['winners']['number'].tolist())
                    prediction = engine.predict_top_5_for_number(int(input_num))
                    
                    st.divider()
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.subheader("Probability Score")
                        st.title(f"{prediction['score']}%")
                        st.progress(prediction['score'] / 100)
                    
                    with col_b:
                        st.subheader("Related Top 5 Picks")
                        st.success(f"**{', '.join(map(str, prediction['top_5']))}**")
                    
                    st.info(f"Analysis: Number {input_num} belongs to series **{prediction.get('series', 'NA')}**. Based on {prediction.get('occurrences_in_series', 0)} historical hits in this cluster.")
                else:
                    st.error("No historical data found in database to run prediction.")

if __name__ == "__main__":
    dashboard = LotteryDashboard()
    dashboard.run()