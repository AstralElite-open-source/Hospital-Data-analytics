"""
Chart generation utilities for Hospital Patient Analytics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Any
import logging

try:
    from ..config import FIGURE_SIZE, DPI, STYLE, COLOR_PALETTES
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import FIGURE_SIZE, DPI, STYLE, COLOR_PALETTES

logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8')
sns.set_style(STYLE)


class ChartGenerator:
    """
    Generates various charts and visualizations for hospital analytics
    """
    
    def __init__(self, color_palette: str = 'primary'):
        """
        Initialize ChartGenerator
        
        Args:
            color_palette: Color palette to use for charts
        """
        self.color_palette = COLOR_PALETTES.get(color_palette, COLOR_PALETTES['primary'])
        
    def create_age_distribution_chart(self, age_data: pd.Series, chart_type: str = 'histogram') -> go.Figure:
        """
        Create age distribution chart
        
        Args:
            age_data: Series containing age data
            chart_type: Type of chart ('histogram', 'box', 'violin')
            
        Returns:
            Plotly figure
        """
        logger.info(f"Creating age distribution chart ({chart_type})")
        
        if chart_type == 'histogram':
            fig = px.histogram(
                x=age_data.dropna(),
                nbins=20,
                title="Age Distribution of Hospital Admissions",
                labels={'x': 'Age', 'y': 'Number of Patients'},
                color_discrete_sequence=[self.color_palette[0]]
            )
            
        elif chart_type == 'box':
            fig = px.box(
                y=age_data.dropna(),
                title="Age Distribution Box Plot",
                labels={'y': 'Age'},
                color_discrete_sequence=[self.color_palette[0]]
            )
            
        elif chart_type == 'violin':
            fig = px.violin(
                y=age_data.dropna(),
                title="Age Distribution Violin Plot",
                labels={'y': 'Age'},
                color_discrete_sequence=[self.color_palette[0]]
            )
            
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16),
            showlegend=False
        )
        
        return fig
        
    def create_disease_prevalence_chart(self, disease_data: Dict, top_n: int = 15) -> go.Figure:
        """
        Create disease prevalence chart
        
        Args:
            disease_data: Dictionary containing disease prevalence data
            top_n: Number of top diseases to show
            
        Returns:
            Plotly figure
        """
        logger.info(f"Creating disease prevalence chart (top {top_n})")
        
        # Sort diseases by count and take top N
        sorted_diseases = sorted(disease_data.items(), key=lambda x: x[1]['count'], reverse=True)[:top_n]
        
        diseases = [item[0] for item in sorted_diseases]
        counts = [item[1]['count'] for item in sorted_diseases]
        percentages = [item[1]['percentage'] for item in sorted_diseases]
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=diseases,
                x=counts,
                orientation='h',
                text=[f'{count} ({pct:.1f}%)' for count, pct in zip(counts, percentages)],
                textposition='inside',
                marker_color=self.color_palette[1]
            )
        ])
        
        fig.update_layout(
            title=f"Top {top_n} Disease Prevalence in Hospital Admissions",
            xaxis_title="Number of Cases",
            yaxis_title="Medical Conditions",
            font=dict(size=10),
            title_font=dict(size=16),
            height=600,
            margin=dict(l=200)  # Increase left margin for long disease names
        )
        
        return fig
        
    def create_temporal_trends_chart(self, temporal_data: Dict) -> go.Figure:
        """
        Create temporal trends chart
        
        Args:
            temporal_data: Dictionary containing temporal analysis data
            
        Returns:
            Plotly figure with subplots
        """
        logger.info("Creating temporal trends chart")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Monthly Patterns', 'Daily Patterns', 'Seasonal Patterns', 'Yearly Trends'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # Monthly patterns
        if 'monthly_patterns' in temporal_data:
            months = list(temporal_data['monthly_patterns'].keys())
            month_counts = list(temporal_data['monthly_patterns'].values())
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            fig.add_trace(
                go.Bar(x=[month_names[int(m)-1] for m in months], y=month_counts,
                      marker_color=self.color_palette[0], name="Monthly"),
                row=1, col=1
            )
        
        # Daily patterns
        if 'daily_patterns' in temporal_data:
            days = list(temporal_data['daily_patterns'].keys())
            day_counts = list(temporal_data['daily_patterns'].values())
            
            fig.add_trace(
                go.Bar(x=days, y=day_counts,
                      marker_color=self.color_palette[1], name="Daily"),
                row=1, col=2
            )
        
        # Seasonal patterns
        if 'seasonal_patterns' in temporal_data:
            seasons = list(temporal_data['seasonal_patterns'].keys())
            season_counts = list(temporal_data['seasonal_patterns'].values())
            
            fig.add_trace(
                go.Pie(labels=seasons, values=season_counts,
                      marker_colors=self.color_palette[:len(seasons)], name="Seasonal"),
                row=2, col=1
            )
        
        # Yearly trends
        if 'yearly_trends' in temporal_data:
            years = sorted(temporal_data['yearly_trends'].keys())
            year_counts = [temporal_data['yearly_trends'][year] for year in years]
            
            fig.add_trace(
                go.Scatter(x=years, y=year_counts, mode='lines+markers',
                          line=dict(color=self.color_palette[2]), name="Yearly"),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Temporal Admission Patterns",
            title_font=dict(size=16),
            showlegend=False
        )
        
        return fig
        
    def create_admission_prediction_chart(self, prediction_data: Dict) -> go.Figure:
        """
        Create admission prediction chart
        
        Args:
            prediction_data: Dictionary containing prediction results
            
        Returns:
            Plotly figure
        """
        logger.info("Creating admission prediction chart")
        
        if 'future_predictions' not in prediction_data:
            return go.Figure().add_annotation(text="No prediction data available")
        
        predictions = prediction_data['future_predictions']
        dates = [pred['date'] for pred in predictions]
        predicted_admissions = [pred['predicted_admissions'] for pred in predictions]
        
        fig = go.Figure()
        
        # Add prediction line
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=predicted_admissions,
                mode='lines+markers',
                name='Predicted Admissions',
                line=dict(color=self.color_palette[0], width=2),
                marker=dict(size=6)
            )
        )
        
        # Add confidence intervals if available
        # This is a placeholder - you would calculate actual confidence intervals
        upper_bound = [int(pred * 1.2) for pred in predicted_admissions]
        lower_bound = [int(pred * 0.8) for pred in predicted_admissions]
        
        fig.add_trace(
            go.Scatter(
                x=dates + dates[::-1],
                y=upper_bound + lower_bound[::-1],
                fill='toself',
                fillcolor='rgba(31, 119, 180, 0.2)',  # Fixed RGBA format
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval',
                hoverinfo="skip"
            )
        )
        
        fig.update_layout(
            title="Hospital Admission Predictions",
            xaxis_title="Date",
            yaxis_title="Predicted Number of Admissions",
            font=dict(size=12),
            title_font=dict(size=16),
            hovermode='x unified'
        )
        
        return fig
        
    def create_risk_factor_analysis_chart(self, risk_data: Dict) -> go.Figure:
        """
        Create risk factor analysis chart
        
        Args:
            risk_data: Dictionary containing risk factor analysis
            
        Returns:
            Plotly figure
        """
        logger.info("Creating risk factor analysis chart")
        
        if 'risk_factor_prevalence' not in risk_data:
            return go.Figure().add_annotation(text="No risk factor data available")
        
        risk_factors = list(risk_data['risk_factor_prevalence'].keys())
        percentages = [risk_data['risk_factor_prevalence'][rf]['percentage'] for rf in risk_factors]
        counts = [risk_data['risk_factor_prevalence'][rf]['count'] for rf in risk_factors]
        
        # Clean up risk factor names
        clean_names = [rf.replace('_', ' ').replace(' ', ' ').strip().title() for rf in risk_factors]
        
        fig = go.Figure(data=[
            go.Bar(
                x=clean_names,
                y=percentages,
                text=[f'{count} patients' for count in counts],
                textposition='outside',
                marker_color=self.color_palette[2]
            )
        ])
        
        fig.update_layout(
            title="Risk Factor Prevalence Among Patients",
            xaxis_title="Risk Factors",
            yaxis_title="Prevalence (%)",
            font=dict(size=12),
            title_font=dict(size=16),
            xaxis_tickangle=-45
        )
        
        return fig
        
    def create_geographical_distribution_chart(self, geo_data: Dict) -> go.Figure:
        """
        Create geographical distribution chart
        
        Args:
            geo_data: Dictionary containing geographical analysis
            
        Returns:
            Plotly figure
        """
        logger.info("Creating geographical distribution chart")
        
        if 'location_distribution' not in geo_data:
            return go.Figure().add_annotation(text="No geographical data available")
        
        locations = list(geo_data['location_distribution'].keys())
        counts = list(geo_data['location_distribution'].values())
        
        # Create pie chart for rural vs urban distribution
        fig = go.Figure(data=[
            go.Pie(
                labels=['Rural' if loc == 'R' else 'Urban' for loc in locations],
                values=counts,
                hole=0.3,
                marker_colors=self.color_palette[:len(locations)]
            )
        ])
        
        fig.update_layout(
            title="Rural vs Urban Patient Distribution",
            font=dict(size=12),
            title_font=dict(size=16),
            annotations=[dict(text='Patients', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
        
    def create_outcome_analysis_chart(self, outcome_data: pd.Series) -> go.Figure:
        """
        Create patient outcome analysis chart
        
        Args:
            outcome_data: Series containing outcome data
            
        Returns:
            Plotly figure
        """
        logger.info("Creating outcome analysis chart")
        
        outcome_counts = outcome_data.value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=outcome_counts.index,
                y=outcome_counts.values,
                marker_color=[
                    '#2ecc71' if outcome == 'DISCHARGE' else '#e74c3c' 
                    for outcome in outcome_counts.index
                ]
            )
        ])
        
        fig.update_layout(
            title="Patient Outcomes Distribution",
            xaxis_title="Outcome",
            yaxis_title="Number of Patients",
            font=dict(size=12),
            title_font=dict(size=16)
        )
        
        return fig
        
    def create_length_of_stay_analysis(self, los_data: pd.Series) -> go.Figure:
        """
        Create length of stay analysis chart
        
        Args:
            los_data: Series containing length of stay data
            
        Returns:
            Plotly figure
        """
        logger.info("Creating length of stay analysis chart")
        
        # Remove outliers for better visualization
        q75, q25 = np.percentile(los_data.dropna(), [75, 25])
        iqr = q75 - q25
        upper_bound = q75 + 1.5 * iqr
        filtered_data = los_data[los_data <= upper_bound]
        
        fig = px.histogram(
            x=filtered_data,
            nbins=30,
            title="Length of Stay Distribution",
            labels={'x': 'Length of Stay (days)', 'y': 'Number of Patients'},
            color_discrete_sequence=[self.color_palette[3]]
        )
        
        # Add mean line
        mean_los = filtered_data.mean()
        fig.add_vline(
            x=mean_los,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_los:.1f} days"
        )
        
        fig.update_layout(
            font=dict(size=12),
            title_font=dict(size=16)
        )
        
        return fig
        
    def save_chart(self, fig: go.Figure, filename: str, format: str = 'html') -> None:
        """
        Save chart to file
        
        Args:
            fig: Plotly figure to save
            filename: Output filename
            format: Output format ('html', 'png', 'pdf', 'svg')
        """
        if format == 'html':
            fig.write_html(filename)
        elif format == 'png':
            fig.write_image(filename, format='png', engine='kaleido')
        elif format == 'pdf':
            fig.write_image(filename, format='pdf', engine='kaleido')
        elif format == 'svg':
            fig.write_image(filename, format='svg', engine='kaleido')
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        logger.info(f"Chart saved to {filename}")


def main():
    """
    Main function to demonstrate chart generation
    """
    print("ChartGenerator module loaded successfully")
    print("Use this class to generate various charts for hospital analytics")


if __name__ == "__main__":
    main()
