import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import calendar
import numpy as np

class Visualizer:
    """
    Handles generation of interactive Plotly charts.
    """
    
    # Theme Configuration
    THEME_COLORS = {
        'background': '#1c1c1c',
        'paper': '#1c1c1c',
        'text': '#e0e0e0',
        'grid': '#333333',
        'primary': '#ef476f',    # Red/Pink (Ebook)
        'secondary': '#06d6a0',  # Green (Audiobook)
        'accent': '#ffd166',     # Yellow (Paperback)
        'grouped': '#118ab2',    # Blue (Aggregated Data)
        'subtext': '#aaaaaa',
        'gradient': ['#ef476f', '#118ab2', '#06d6a0']
    }

    # Format Colors
    FORMAT_COLORS = {
        'ebook': '#ef476f',     # Red/Pink
        'paperback': '#ffd166', # Yellow
        'audiobook': '#06d6a0', # Green
        'kindle': '#ef476f',    # Fallback
        'paper': '#ffd166'      # Fallback
    }

    # Language Colors
    LANGUAGE_COLORS = {
        'en': '#118ab2', 'English': '#118ab2',     # Blue
        'it': '#ffd166', 'Italian': '#ffd166',     # Yellow
        'ja': '#ef476f', 'Japanese': '#ef476f',    # Red/Pink
        'fr': '#06d6a0', 'French': '#06d6a0',      # Green
        'es': '#5f27cd', 'Spanish': '#5f27cd',     # Purple (Keep distinctive)
        'de': '#ff6b6b', 'German': '#ff6b6b',      # Red
        'ru': '#ff9f43', 'Russian': '#ff9f43',     # Orange
        'zh': '#ee5253', 'Chinese': '#ee5253',     # Red-Orange
        'other': '#8395a7', 'Other': '#8395a7'     # Grey
    }
    
    # Standard Plot Dimensions
    PLOT_WIDTH = 1200
    PLOT_HEIGHT = 700

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self._set_global_theme()

    def _set_global_theme(self):
        """Configure global Plotly defaults."""
        import plotly.io as pio
        import plotly.graph_objects as go
        
        # Modify the default template directly
        pio.templates["kograph_dark"] = go.layout.Template(
            layout=go.Layout(
                paper_bgcolor=self.THEME_COLORS['paper'],
                plot_bgcolor=self.THEME_COLORS['background'],
                font=dict(
                    family="Inter, sans-serif",
                    color=self.THEME_COLORS['text']
                ),
                xaxis=dict(gridcolor=self.THEME_COLORS['grid']),
                yaxis=dict(gridcolor=self.THEME_COLORS['grid']),
                colorway=self.THEME_COLORS['gradient']
            )
        )
        
        # Merge with plotly_dark
        pio.templates.default = "plotly_dark+kograph_dark"

    def plot_weekly_activity(self, year: int = None):
        """
        Stacked Bar chart of total reading hours per week (or month for >5 years), split by format.
        Args:
            year (int, optional): Filter data for a specific year.
        """
        df = self.data.copy()
        
        # Filter by year if specified
        if year:
            df = df[df['year'] == year]
        
        if df.empty:
            print(f"Warning: No data found for year {year}")
            return None

        # Check year span to decide on grouping
        min_year = df['year'].min()
        max_year = df['year'].max()
        year_span = max_year - min_year
        
        if year_span > 5:
            period = 'M'
            title = 'Monthly Reading Activity'
            x_label = 'Month'
        else:
            period = 'W'
            title = 'Weekly Reading Activity'
            x_label = 'Week'

        # Ensure datetime column exists
        if 'start_datetime' not in df.columns:
             if 'date' in df.columns:
                df['start_datetime'] = pd.to_datetime(df['date'])
        
        # Create period column
        df['period_date'] = df['start_datetime'].dt.to_period(period).dt.start_time
        
        # Aggregate duration and book titles per period and format
        aggregated = df.groupby(['period_date', 'format']).agg({
            'duration': 'sum',
            'title': lambda x: '<br>'.join(sorted(list(set(x)))[:5]) + ('...' if len(set(x)) > 5 else '')
        }).reset_index()
        
        aggregated['hours'] = aggregated['duration'] / 3600
        aggregated['books_list'] = aggregated['title']
        
        aggregated['formatted_time'] = aggregated.apply(
            lambda x: f"{int(x['duration'] // 3600)}h {int((x['duration'] % 3600) // 60)}m", 
            axis=1
        )
        
        # Create Stacked Bar Plot
        fig = px.bar(
            aggregated, 
            x='period_date', 
            y='hours',
            color='format', # Stack by format
            title=title,
            labels={'hours': 'Hours Read', 'period_date': x_label, 'format': 'Format'},
            custom_data=['formatted_time', 'books_list', 'format'],
            color_discrete_map=self.FORMAT_COLORS # Apply explicit colors
        )
        
        # Styling
        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            showlegend=True, # Show legend for formats
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            title_x=0.5,
            title_xanchor='center',
            title_y=0.95,
            hovermode="x", # Unified hover might be better for stacked bars? Or sticking to x
            # For stacked bars, "hovermode='x'" shows all stack items at that x.
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50), # Consistent margins
            xaxis=dict(
                showgrid=False,
                title=None
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=self.THEME_COLORS['grid'],
                title='Reading Time (hours)'
            )
        )
        
        fig.update_traces(
            marker_line_width=0,
            # Use customdata[0] for formatted time, customdata[1] for books
            hovertemplate="<br><b>%{customdata[2]}</b><br><b>Time</b>: %{customdata[0]}<br><b>Books:</b><br>%{customdata[1]}<extra></extra>",
            hoverlabel=dict(bgcolor="black") # Black background
        )
        
        return fig

    def plot_reading_calendar(self, year: int = None):
        """
        3x4 Month Grid Scatter plot for reading habits.
        """
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]
        else:
            target_year = df['year'].max()
            df = df[df['year'] == target_year]
            year = target_year

        title = 'Reading Calendar'
        
        # Exclude Paperback AND Manual Audiobooks/Ebooks (Numbers)
        # We need daily data. Manual imports (Numbers) are synthetic averages or single sessions.
        
        # 1. Remove Paperbacks
        if 'format' in df.columns:
            df = df[df['format'] != 'paperback']

        # 2. Remove Books from Numbers (Simple Audiobooks included)
        # This covers Ebooks AND Audiobooks from Numbers.
        # Detailed Audiobooks (CSV) do NOT have data_source='numbers' (usually null or other)
        if 'data_source' in df.columns:
             df = df[df['data_source'] != 'numbers']

        # Exclude manual ebooks (negative id_book) - Fallback if data_source missing
        if 'id_book' in df.columns and 'format' in df.columns:
             mask = (df['format'] == 'ebook') & (df['id_book'] < 0)
             df = df.loc[~mask]

        if df.empty:
            return None
            
        # Prepare subplots
        fig = make_subplots(
            rows=3, cols=4, 
            subplot_titles=[calendar.month_name[i] for i in range(1, 13)],
            vertical_spacing=0.08,
            horizontal_spacing=0.03
        )

        daily = df.groupby('date').agg({
            'duration': 'sum',
            'title': lambda x: '<br>'.join(sorted(list(set(x)))[:5]) + ('...' if len(set(x)) > 5 else '')
        }).reset_index()
        
        daily['minutes'] = daily['duration'] / 60
        daily['date'] = pd.to_datetime(daily['date'])
        daily['books_list'] = daily['title']
        
        # Max reading for color normalization
        max_reading = daily['minutes'].max() if not daily.empty else 1
        
        # Find global max day for highlighting
        max_day_date = daily.loc[daily['minutes'].idxmax(), 'date'] if not daily.empty else None

        # Identify the last month with data to attach the color scale
        last_active_month = int(df['month'].max()) if 'month' in df.columns and not df.empty else 12

        # Iterate through months
        for month in range(1, 13):
            row = (month - 1) // 4 + 1
            col = (month - 1) % 4 + 1
            
            # Generate full dates for this month
            _, num_days = calendar.monthrange(year, month)
            dates = pd.date_range(start=f"{year}-{month:02d}-01", end=f"{year}-{month:02d}-{num_days}")
            
            month_df = pd.DataFrame({'date': dates})
            month_df = month_df.merge(daily[['date', 'minutes', 'books_list']], on='date', how='left').fillna({'minutes': 0, 'books_list': ''})
            
            # Coordinates
            month_df['day_of_week'] = month_df['date'].dt.dayofweek # 0=Mon
            
            # Week of month (0-based index)
            first_day_weekday = month_df.iloc[0]['date'].dayofweek
            month_df['day_idx'] = month_df['date'].dt.day - 1
            month_df['week_of_month'] = (month_df['day_idx'] + first_day_weekday) // 7
            
            # Formatting
            month_df['formatted_time'] = month_df.apply(
                lambda x: f"{int(x['minutes'] // 60)}h {int(x['minutes'] % 60)}m" if x['minutes'] > 0 else "0m", 
                axis=1
            )
            
            month_df['hover_text'] = month_df.apply(
                lambda x: (
                    f"<b>{x['date'].strftime('%b %d')}</b><br>{x['formatted_time']}<br><br><b>Books:</b><br>{x['books_list']}"
                    if x['minutes'] > 0 else
                    f"<b>{x['date'].strftime('%b %d')}</b><br>No Reading"
                ), 
                axis=1
            )
            
            # Find last month with data to show scale
            last_active_month = df['month'].max() if not df.empty else 12
            
            # Show legend (colorbar) on the last month that has data
            # If data ends in Oct, show on Oct. If full year, show on Dec.
            # If a month has no data, active_df is empty so the trace coupled to show_scale won't be added.
            # We must ensure we attach the scale to a month that HAS active data.
            # So last_active_month must be derived from rows where duration > 0.
            
            # Calculate this ONCE outside loop would be better but let's do it inline for min change
            # Optimization: Calculate outside
            
            show_scale = (month == last_active_month)
            
            # Split into Active (Reading) and Inactive (Empty)
            active_df = month_df[month_df['minutes'] > 0].copy()
            inactive_df = month_df[month_df['minutes'] == 0].copy()

            # 1. Inactive Trace (No Hover)
            fig.add_trace(
                go.Scatter(
                    x=inactive_df['day_of_week'],
                    y=5 - inactive_df['week_of_month'],
                    mode='markers',
                    marker=dict(
                        size=14,
                        color='#333333', # Empty color
                        line=dict(width=1, color=self.THEME_COLORS['background'])
                    ),
                    hoverinfo='skip',
                    showlegend=False
                ),
                row=row, col=col
            )

            # 2. Active Trace (With Hover)
            if not active_df.empty:
                # Line styling logic: Highlight Max Day
                # We need to compute line colors and widths row by row because Plotly expects arrays or scalar
                # Or we can use apply
                def get_line_style(row_date):
                    if max_day_date and row_date == max_day_date:
                        return self.THEME_COLORS['accent'], 2 # Accent color, thicker
                    return self.THEME_COLORS['text'], 1 # Default, thin

                lines = active_df['date'].apply(get_line_style)
                active_df['line_color'] = lines.apply(lambda x: x[0])
                active_df['line_width'] = lines.apply(lambda x: x[1])
                
                fig.add_trace(
                    go.Scatter(
                        x=active_df['day_of_week'],
                        y=5 - active_df['week_of_month'], 
                        mode='markers',
                        marker=dict(
                            size=14,
                            color=active_df['minutes'],
                            colorscale=[
                                [0, '#333333'], # Should not happen for active
                                [0.01, '#2d3436'],
                                [1, self.THEME_COLORS['primary']]
                            ],
                            cmin=0,
                            cmax=max_reading,
                            showscale=show_scale,
                            colorbar=dict(
                                title=dict(
                                    text="Reading Time (minutes)",
                                    side="right"
                                ),
                                thickness=15,
                                len=0.7,
                                y=0.5
                            ) if show_scale else None,
                            line=dict(
                                width=active_df['line_width'], 
                                color=active_df['line_color']
                            )
                        ),
                        text=active_df['hover_text'],
                        hoverinfo='text',
                        showlegend=False
                    ),
                    row=row, col=col
                )
            
            # Clean up axes for this subplot
            fig.update_xaxes(
                showgrid=False, zeroline=False, showticklabels=False, 
                range=[-0.5, 6.5], row=row, col=col
            )
            fig.update_yaxes(
                showgrid=False, zeroline=False, showticklabels=False, 
                range=[-0.5, 6.5], row=row, col=col
            )
            
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', y=0.98),
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=100, l=50, r=50, b=50),
            hoverlabel=dict(bgcolor="black")
        )
        
        return fig

    def plot_time_of_day(self, year: int = None):
        """
        Bar chart showing reading distribution across hours of the day (0-23).
        """
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]
        
        title = 'Time of Day Distribution'

        if df.empty:
            return None

        # Exclude Paperback AND Manual Ebooks (Numbers)
        if 'format' in df.columns:
            # 1. Remove Paperbacks
            df = df[df['format'] != 'paperback']
            
            # 2. Remove Ebooks AND Audiobooks that are from Numbers
            # Numbers data (manual entry) often has default 12:00 PM time, which skews the distribution.
            if 'data_source' in df.columns:
                 # Exclude ANY format if source is 'numbers' for this plot? 
                 # Or specifically exclude Ebook and Audiobook from Numbers.
                 # Let's target both to be safe.
                 df = df[~((df['format'].isin(['ebook', 'audiobook'])) & (df['data_source'] == 'numbers'))]

        # Group by hour AND format
        # We need to ensure we have all hours for all present formats?
        # Actually px.bar handles missing categories often, but let's aggregate first.
        hourly = df.groupby(['hour', 'format'])['duration'].sum().reset_index()
        
        # Calculate Percentage (relative to Total Duration of displayed formats)
        total_duration = hourly['duration'].sum()
        hourly['percentage'] = (hourly['duration'] / total_duration * 100) if total_duration > 0 else 0
        hourly['hours'] = hourly['duration'] / 3600
        
        # Formatting for tooltip
        hourly['formatted_time'] = hourly.apply(
            lambda x: f"{int(x['duration'] // 3600)}h {int((x['duration'] % 3600) // 60)}m", 
            axis=1
        )
        
        # Create Stacked Bar Plot
        fig = px.bar(
            hourly, 
            x='hour', 
            y='percentage',
            color='format',
            title=title,
            labels={'percentage': 'Percentage (%)', 'hour': 'Hour of Day', 'format': 'Format'},
            custom_data=['formatted_time', 'percentage', 'format'],
            color_discrete_map=self.FORMAT_COLORS
        )
        
        # Styling
        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            title_x=0.5,
            title_xanchor='center',
            title_y=0.95,
            hovermode="x", # Shows all stacks for that hour
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=1,
                range=[-0.5, 23.5],
                title="Hour of Day",
                showgrid=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=self.THEME_COLORS['grid'],
                title='Percentage of Reading Time (%)',
                ticksuffix="%",
                rangemode='tozero'
            )
        )
        
        fig.update_traces(
            marker_line_width=0,
            hovertemplate="<br><b>Format:</b> %{customdata[2]}<br><b>Share</b>: %{y:.1f}%<br><b>Time</b>: %{customdata[0]}<extra></extra>",
            hoverlabel=dict(bgcolor="black")
        )
        
        return fig

    def plot_reading_distribution(self, year: int = None):
        """
        Histogram of daily reading minutes (Aggregated across formats).
        """
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]
        
        title = 'Daily Reading Time Distribution'
        
        # Exclude Paperback data to avoid synthetic peaks and maintain consistency with "Activity Patterns"
        if 'format' in df.columns:
            df = df[df['format'] != 'paperback']
        
        if df.empty:
            return None

        # Group by date ONLY (Aggregate formats)
        daily = df.groupby('date')['duration'].sum().reset_index()
        daily['minutes'] = daily['duration'] / 60
        
        if daily.empty:
            return None

        # Calculate stats
        mean_val = daily['minutes'].mean()
        median_val = daily['minutes'].median()

        # Create Histogram
        fig = px.histogram(
            daily, 
            x='minutes', 
            nbins=30, # Moderate bin count
            title=title,
            labels={'minutes': 'Daily Minutes'},
            color_discrete_sequence=[self.THEME_COLORS['grouped']]
        )
        
        # Add Mean Line
        fig.add_vline(x=mean_val, line_width=2, line_dash="dash", line_color=self.THEME_COLORS['secondary'])
        fig.add_annotation(x=mean_val, y=0.95, yref='paper', text=f"Mean: {mean_val:.0f}m", showarrow=False, xanchor='left', font=dict(color=self.THEME_COLORS['secondary']))
        
        # Add Median Line
        fig.add_vline(x=median_val, line_width=2, line_dash="dot", line_color=self.THEME_COLORS['accent'])
        fig.add_annotation(x=median_val, y=0.85, yref='paper', text=f"Median: {median_val:.0f}m", showarrow=False, xanchor='left', font=dict(color=self.THEME_COLORS['accent']))
        
        # Styling
        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            showlegend=False,
            title_x=0.5,
            title_xanchor='center',
            title_y=0.95,
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            xaxis=dict(
                title='Daily Reading Minutes',
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=False
            ),
            yaxis=dict(
                title='Count of Days',
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=True
            ),
            bargap=0.1
        )
        
        fig.update_traces(
            marker_line_width=0,
            hoverlabel=dict(bgcolor="black"),
            hovertemplate="<b>%{x}</b> min<br>Days: %{y}<extra></extra>"
        )
        
        return fig

    def _calculate_streaks(self, df: pd.DataFrame, min_minutes=10) -> list[int]:
        """
        Calculate list of streak lengths (consecutive days with >= min_minutes reading).
        """
        if df.empty:
            return []

        # daily sums
        daily = df.groupby('date')['duration'].sum()
        # filter days meeting threshold
        valid_days = daily[daily >= min_minutes * 60].index
        valid_days = pd.Series(sorted(valid_days))
        
        if valid_days.empty:
            return []
            
        streaks = []
        current_streak = 1
        
        for i in range(1, len(valid_days)):
            # Check if consecutive day
            if (valid_days.iloc[i] - valid_days.iloc[i-1]).days == 1:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1
        streaks.append(current_streak)
        
        return streaks

    def plot_streaks(self, year: int = None):
        """
        Histogram of reading streaks and summary stats.
        """
        df = self.data.copy()
        if year:
            df = df[df['year'] == year]
        
        title = 'Reading Streaks'
        
        # Exclude Paperback
        if 'format' in df.columns:
            df = df[df['format'] != 'paperback']

        # Exclude Manual Data (Numbers) - Simple Audiobooks/Ebooks
        if 'data_source' in df.columns:
             df = df[df['data_source'] != 'numbers']

        # Exclude manual ebooks (negative id_book)
        if 'id_book' in df.columns and 'format' in df.columns:
             mask = (df['format'] == 'ebook') & (df['id_book'] < 0)
             df = df.loc[~mask]

        streaks = self._calculate_streaks(df)
        
        if not streaks:
            return None
            
        # Stats
        longest = max(streaks)
        avg_streak = sum(streaks) / len(streaks)
        
        # Prepare for Histogram
        # We want to count how many times each streak length occurred
        streak_counts = pd.Series(streaks).value_counts().reset_index()
        streak_counts.columns = ['length', 'count']
        streak_counts = streak_counts.sort_values('length')
        
        fig = px.bar(
            streak_counts, 
            x='length', 
            y='count',
            color='length', # Map color to streak length
            title=title,
            # Used gradient from accent (Yellow) to secondary (Pink)
            color_continuous_scale=[
                [0, self.THEME_COLORS['accent']], 
                [1, self.THEME_COLORS['secondary']]
            ]
            # Removed text='count' to hide numbers inside bins
        )
        
        # Annotation text
        stats_text = (
            f"<b>Longest Streak:</b> {longest} days<br>"
            f"<b>Average Streak:</b> {avg_streak:.1f} days<br>"
        )
        
        fig.add_annotation(
            x=0.98,
            y=0.98,
            xref="paper",
            yref="paper",
            text=stats_text,
            showarrow=False,
            font=dict(size=14, color=self.THEME_COLORS['text']),
            align="right",
            bgcolor=self.THEME_COLORS['background'],
            bordercolor=self.THEME_COLORS['subtext'],
            borderwidth=1,
            borderpad=10
        )

        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            title_x=0.5,
            title_xanchor='center',
            title_y=0.95,
            showlegend=False,
            coloraxis_showscale=False, # Hide the color bar
            xaxis=dict(
                title='Streak Length (Days)',
                dtick=1, # Show every integer
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=False
            ),
            yaxis=dict(
                title='Count',
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=True
            )
        )
        
        fig.update_traces(
            # marker_color removed as it overrides color_continuous_scale
            marker_line_width=0,
            # Updated hovertemplate to match weekly_activity style
            hovertemplate="<br><b>Length</b>: %{x} days<br><b>Count</b>: %{y}<extra></extra>",
            hoverlabel=dict(bgcolor="black")
        )
        
        return fig

    def _calculate_daily_streaks_map(self, df: pd.DataFrame, min_minutes=10) -> dict:
        """
        Map each valid reading date to its current streak length.
        Returns: {pd.Timestamp: int_streak_length}
        """
        if df.empty:
            return {}

        daily = df.groupby('date')['duration'].sum()
        valid_dates = sorted(daily[daily >= min_minutes * 60].index)
        
        if not valid_dates:
            return {}
            
        streak_map = {}
        current_streak = []
        
        # We need to iterate and build streaks.
        # This logic is slightly different: we want to assign the streak length 
        # to ALL days in that streak.
        
        # Iterate through dates
        temp_streak = [valid_dates[0]]
        
        for i in range(1, len(valid_dates)):
            curr = valid_dates[i]
            prev = valid_dates[i-1]
            
            if (curr - prev).days == 1:
                # Part of same streak
                temp_streak.append(curr)
            else:
                # Streak ended. Assign lengths.
                length = len(temp_streak)
                for d in temp_streak:
                    streak_map[pd.to_datetime(d)] = length
                # Start new streak
                temp_streak = [curr]
        
        # Final streak
        length = len(temp_streak)
        for d in temp_streak:
            streak_map[pd.to_datetime(d)] = length
            
        return streak_map

    def plot_streak_calendar(self, year: int = None):
        """
        3x4 Month Grid Scatter plot showing streak lengths.
        """
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]
        else:
            target_year = df['year'].max()
            df = df[df['year'] == target_year]
            year = target_year
            
        title = 'Streak Calendar'

        # Exclude Paperback AND Manual Data (Numbers)
        # 1. Remove Paperbacks
        if 'format' in df.columns:
            df = df[df['format'] != 'paperback']
            
        # 2. Remove Books from Numbers (Simple Audiobooks/Ebooks)
        if 'data_source' in df.columns:
            df = df[df['data_source'] != 'numbers']

        if df.empty:
            return None
        
        # Pre-calc books per day for tooltip
        daily_books = df.groupby('date').agg({
            'title': lambda x: '<br>'.join(sorted(list(set(x)))[:5]) + ('...' if len(set(x)) > 5 else '')
        }).reset_index()
        daily_books['date'] = pd.to_datetime(daily_books['date'])
        daily_books['books_list'] = daily_books['title']

        # Calculate streaks
        streak_map = self._calculate_daily_streaks_map(df)
        if not streak_map:
            return None

        max_streak = max(streak_map.values())

        # Prepare subplots
        fig = make_subplots(
            rows=3, cols=4, 
            subplot_titles=[calendar.month_name[i] for i in range(1, 13)],
            vertical_spacing=0.08,
            horizontal_spacing=0.03
        )

        # Iterate through months
        for month in range(1, 13):
            row = (month - 1) // 4 + 1
            col = (month - 1) % 4 + 1
            
            _, num_days = calendar.monthrange(year, month)
            dates = pd.date_range(start=f"{year}-{month:02d}-01", end=f"{year}-{month:02d}-{num_days}")
            
            month_df = pd.DataFrame({'date': dates})
            
            # Map streak lengths
            month_df['streak'] = month_df['date'].map(streak_map).fillna(0).astype(int)
            
            # Merge book info
            month_df = month_df.merge(daily_books[['date', 'books_list']], on='date', how='left').fillna({'books_list': ''})
            
            # Coordinates
            month_df['day_of_week'] = month_df['date'].dt.dayofweek
            
            first_day_weekday = month_df.iloc[0]['date'].dayofweek
            month_df['day_idx'] = month_df['date'].dt.day - 1
            month_df['week_of_month'] = (month_df['day_idx'] + first_day_weekday) // 7
            
            month_df['hover_text'] = month_df.apply(
                lambda x: (
                    f"<b>{x['date'].strftime('%b %d')}</b><br>Streak: {x['streak']} days<br><br><b>Books:</b><br>{x['books_list']}"
                    if x['streak'] > 0 else 
                    f"<b>{x['date'].strftime('%b %d')}</b><br>No Streak"
                ),
                axis=1
            )
            
            # Show legend only on last
            show_scale = (month == 12)
            
            # Split into Active (Streak) and Inactive (No Streak)
            active_df = month_df[month_df['streak'] > 0].copy()
            inactive_df = month_df[month_df['streak'] == 0].copy()

            # 1. Inactive Trace
            fig.add_trace(
                go.Scatter(
                    x=inactive_df['day_of_week'],
                    y=5 - inactive_df['week_of_month'],
                    mode='markers',
                    marker=dict(
                        size=14,
                        color='#333333',
                        line=dict(width=1, color=self.THEME_COLORS['background'])
                    ),
                    hoverinfo='skip',
                    showlegend=False
                ),
                row=row, col=col
            )

            # 2. Active Trace
            if not active_df.empty:
                active_df['line_color'] = self.THEME_COLORS['text']
                
                fig.add_trace(
                    go.Scatter(
                        x=active_df['day_of_week'],
                        y=5 - active_df['week_of_month'], 
                        mode='markers',
                        marker=dict(
                            size=14,
                            color=active_df['streak'],
                            colorscale=[
                                [0, '#333333'], 
                                [0.01, self.THEME_COLORS['accent']], # Yellow start
                                [1, self.THEME_COLORS['secondary']]  # Pink end
                            ],
                            cmin=0,
                            cmax=max_streak,
                            showscale=show_scale,
                            colorbar=dict(
                                title=dict(
                                    text="Streak Length (days)",
                                    side="right"
                                ),
                                thickness=15,
                                len=0.7,
                                y=0.5
                            ) if show_scale else None,
                            line=dict(width=1, color=active_df['line_color'])
                        ),
                        text=active_df['hover_text'],
                        hoverinfo='text',
                        showlegend=False
                    ),
                    row=row, col=col
                )
            
            fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 6.5], row=row, col=col)
            fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 6.5], row=row, col=col)

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', y=0.98),
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=100, l=50, r=50, b=50),
            hoverlabel=dict(bgcolor="black")
        )
        
        return fig

    # Book colors for consistent visualization
    BOOK_COLORS = [
        '#ff595e', '#ff924c', '#ffca3a', '#c5ca30', '#8ac926',
        '#36949d', '#1982c4', '#4267ac', '#565aa0', '#6a4c93'
    ]

    def _calculate_book_segments(self, df: pd.DataFrame, gap_days=7) -> pd.DataFrame:
        """
        Split book reading into segments if there are gaps > gap_days.
        Returns DataFrame suitable for px.timeline.
        """
        segments = []
        
        # Group by book
        for book_id, book_df in df.groupby('id_book'):
            # Get metadata from first row
            title = book_df['title'].iloc[0]
            fmt = book_df['format'].iloc[0] if 'format' in book_df.columns else 'kindle'
            
            # Get all unique reading dates
            dates = sorted(book_df['date'].unique())
            if not dates:
                continue
                
            dates = [pd.to_datetime(d) for d in dates]
            
            # Global dates for tooltip
            global_start = dates[0]
            global_end = dates[-1]
            
            # Find segments
            current_start = dates[0]
            current_end = dates[0]
            
            for i in range(1, len(dates)):
                diff = (dates[i] - dates[i-1]).days
                
                if diff > gap_days:
                    # End previous segment
                    segments.append({
                        'Title': title,
                        'Start': current_start,
                        'Finish': current_end + pd.Timedelta(days=1), # Add 1 day for visibility
                        'GlobalStart': global_start,
                        'GlobalFinish': global_end,
                        'Format': fmt,
                        'id_book': book_id
                    })
                    # Start new segment
                    current_start = dates[i]
                    current_end = dates[i]
                else:
                    # Extend segment
                    current_end = dates[i]
            
            # Add final segment
            segments.append({
                'Title': title,
                'Start': current_start,
                'Finish': current_end + pd.Timedelta(days=1),
                'GlobalStart': global_start,
                'GlobalFinish': global_end,
                'Format': fmt,
                'id_book': book_id
            })
            
        return pd.DataFrame(segments)

    def plot_book_timeline(self, year: int = None):
        """
        Gantt chart of book reading timeline with smart labeling.
        """
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]

        title = 'Reading Timeline'

        if df.empty:
            return None

        segments_df = self._calculate_book_segments(df)
        
        if segments_df.empty:
            return None
            
        # Determine global time range to check boundaries
        min_date = segments_df['Start'].min()
        max_date = segments_df['Finish'].max()
        total_days_span = (max_date - min_date).days
        if total_days_span < 1: total_days_span = 1
        
        # Sort by Start date
        segments_df = segments_df.sort_values('Start', ascending=False)
        
        # Prepare Data Frames
        reading_df = segments_df.copy()
        
        # Create Spans Data (Background)
        # One row per book representing the full duration (Start to Finish)
        spans_df = segments_df[['Title', 'GlobalStart', 'GlobalFinish', 'Format']].drop_duplicates()
        
        # Create VisualFinish for plotting (Finish + 1 day to cover the last day)
        spans_df['VisualFinish'] = spans_df['GlobalFinish'] + pd.Timedelta(days=1)
        
        # Assign colors
        unique_books = segments_df['Title'].unique()
        color_map = {}
        for i, book_title in enumerate(unique_books):
            color_map[book_title] = self.BOOK_COLORS[i % len(self.BOOK_COLORS)]
        
        # 1. Plot Background Spans (Opacity 0.3, Interactive)
        # This layer handles the tooltip and covers the Full Duration (Start to VisualFinish)
        fig = px.timeline(
            spans_df, 
            x_start="GlobalStart", 
            x_end="VisualFinish", 
            y="Title",
            color="Title",
            color_discrete_map=color_map,
            opacity=0.3,
            title=title,
            pattern_shape="Format",
            pattern_shape_map={'ebook': '', 'paperback': '/', 'audiobook': '.'},
            custom_data=['GlobalStart', 'GlobalFinish'] # Explicit columns for tooltip
        )
        
        # 2. Plot Reading Segments (Opacity 1.0, Non-Interactive)
        # This layer shows actual reading sessions. Hover is skipped so mouse hits the background.
        fig_reading = px.timeline(
            reading_df, 
            x_start="Start", 
            x_end="Finish", 
            y="Title",
            color="Title",
            color_discrete_map=color_map,
            opacity=1.0,
            pattern_shape="Format",
            pattern_shape_map={'ebook': '', 'paperback': '/', 'audiobook': '.'}
        )
        
        # Set top layer to ignore hover, allowing fall-through to background
        fig_reading.update_traces(hoverinfo='skip')
        
        # Add reading traces to main fig
        fig.add_traces(fig_reading.data)
        
        # Calculate Annotations (Smart Text Placement per Book)
        annotations = []
        char_days_width = 2.5 
        
        for _, row in spans_df.iterrows():
            title_text = row['Title']
            start = row['GlobalStart']
            end = row['VisualFinish'] # Use VisualFinish for placement logic
            duration = (end - start).days
            
            text_len_days = len(title_text) * char_days_width
            
            # Decide position
            # 1. Inside
            if duration > (text_len_days + total_days_span * 0.02): 
                x_pos = start + (end - start) / 2
                x_anchor = 'center'
                text_color = 'white' 
                show_arrow = False
            else:
                # 2. Try Right
                space_right = (max_date - end).days
                if space_right > (text_len_days + total_days_span * 0.02):
                    x_pos = end + pd.Timedelta(days=total_days_span * 0.01) 
                    x_anchor = 'left'
                    text_color = self.THEME_COLORS['text']
                    show_arrow = False
                else:
                    # 3. Must go Left
                    x_pos = start - pd.Timedelta(days=total_days_span * 0.01)
                    x_anchor = 'right'
                    text_color = self.THEME_COLORS['text']
                    show_arrow = False
            
            annotations.append(dict(
                x=x_pos,
                y=title_text, 
                text=title_text,
                showarrow=show_arrow,
                xanchor=x_anchor,
                yanchor='middle',
                font=dict(color=text_color, size=11),
                bgcolor=None
            ))

        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH + 200, 
            height=max(500, len(unique_books) * 35 + 100),
            margin=dict(t=80, l=50, r=50, b=50), 
            title_x=0.5,
            showlegend=False, 
            xaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                title=None
            ),
            yaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                title=None,
                showticklabels=False, 
                automargin=True
            ),
            annotations=annotations
        )
        
        # Order
        fig.update_yaxes(categoryorder='array', categoryarray=unique_books[::-1])
        
        # Use Year in axis format for All Time view
        axis_format = "%b %Y" if not year else "%b"
        fig.update_xaxes(tickformat=axis_format)

        # Update Tooltip
        # customdata[0] is GlobalStart, customdata[1] is GlobalFinish
        fig.update_traces(
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Start: %{customdata[0]|%b %d, %Y}<br>End: %{customdata[1]|%b %d, %Y}<extra></extra>",
            hoverlabel=dict(bgcolor="black")
        )
        
        # Custom Legend for Format
        # 1. Hide default legend (titles)
        for trace in fig.data:
            trace.showlegend = False
            
        # 2. Add dummy traces for "Kindle" and "Physical Book"
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            name='Kindle',
            marker=dict(color=self.THEME_COLORS['text'], pattern_shape=''),
            showlegend=True
        ))
        
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            name='Paperback',
            marker=dict(color=self.THEME_COLORS['text'], pattern_shape='/'),
            showlegend=True
        ))
        
        # Dynamic Width for Horizontal Scrolling (Fixed Height)
        pixels_per_day = 4 # ~1500px per year
        dynamic_width = max(self.PLOT_WIDTH, total_days_span * pixels_per_day)
        
        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=dynamic_width,
            height=self.PLOT_HEIGHT, # Fixed height as requested
            autosize=False,
            margin=dict(t=80, l=50, r=50, b=50), # Minimal label margin, relying on on-chart labels
            title=dict(text=title, x=0.5, xanchor='center'), # Title centered on full width
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                bgcolor='rgba(0,0,0,0)'
            ),
            xaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                title=None,
                side='top' # Put dates on top for better readability on long scroll? Or keep bottom. Bottom is standard.
            ),
            yaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                title=None,
                showticklabels=False, 
                automargin=True
            ),
            annotations=annotations
        )

        return fig


        
    def plot_cumulative_pages(self, year: int = None):
        """
        Stacked Area chart of cumulative pages read over time, split by format.
        """
        df = self.data.copy()
        if 'format' not in df.columns:
            df['format'] = 'kindle'
            
        if year:
            df = df[df['year'] == year]
        
        title = 'Cumulative Pages Read'

        if df.empty:
            return None

        # Ensure pages_read column exists
        if 'pages_read' not in df.columns:
            df['pages_read'] = 0

        # Logic for Audiobooks: 60 seconds = 1 page
        if 'format' in df.columns and 'duration' in df.columns:
            # We use loc to handle the assignment safely
            audio_mask = df['format'] == 'audiobook'
            if audio_mask.any():
                # duration is in seconds. 60s = 1 page.
                df.loc[audio_mask, 'pages_read'] = df.loc[audio_mask, 'duration'] / 60

        # 1. Aggregate Daily Pages by Format
        daily_pages = df.groupby(['date', 'format'])['pages_read'].sum().reset_index()
        
        # 2. Pivot to ensure full date coverage for all formats (fill 0)
        if daily_pages.empty:
            return None

        # Create full date range to handle gaps
        min_date = daily_pages['date'].min()
        max_date = daily_pages['date'].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D').date
        
        pivot_df = daily_pages.pivot(index='date', columns='format', values='pages_read').reindex(all_dates, fill_value=0).fillna(0)
        pivot_df.index.name = 'date'
        
        # 3. Calculate Cumulative Sum
        cumulative_df = pivot_df.cumsum()
        
        # 4. Melt back for Plotly
        plot_df = cumulative_df.reset_index().melt(
            id_vars='date', 
            var_name='Format', 
            value_name='Cumulative Pages'
        )
        
        # Determine Stacking Order (Largest Total at Bottom)
        # We want the format with the highest final cumulative value to be the first in the list (bottom of stack)
        final_totals = cumulative_df.iloc[-1].sort_values(ascending=False)
        sorted_formats = final_totals.index.tolist()
        
        # Plot
        fig = px.area(
            plot_df,
            x='date',
            y='Cumulative Pages',
            color='Format',
            title=title,
            category_orders={'Format': sorted_formats}, # Apply specific order
            color_discrete_map=self.FORMAT_COLORS
        )
        
        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            title_x=0.5,
            title_xanchor='center',
            title_y=0.95,
            xaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=True
            ),
            yaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=True,
                title='Total Pages'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_traces(
            hoverlabel=dict(bgcolor="black"),
            hovertemplate="<b>%{x}</b><br>%{y:.0f} Pages<extra></extra>"
        )
        
        return fig

    def plot_books_completed(self, year: int = None):
        """
        Bar chart of books completed over time.
        Yearly: Aggregated by Month.
        All Time: Aggregated by Quarter.
        Completion Date = Last date a book was read.
        """
        df = self.data.copy()
    
        # Filter for completed books only
        if 'is_completed' in df.columns:
            df = df[df['is_completed'] == True]
    
        # 1. Determine Finish Date and Format for each book
        # Group by book and get the last reading date + format (assuming format constant per book)
        books_finished = df.groupby(['id_book', 'title']).agg({
            'start_datetime': 'max',
            'format': 'first' # Get format
        }).reset_index()
        books_finished.columns = ['id_book', 'title', 'finish_date', 'format']
        
        # 2. Filter by Year
        if year:
            books_finished = books_finished[books_finished['finish_date'].dt.year == year]
            freq = 'MS' # Month Start for cleaner alignment
        else:
            freq = 'QS' # Quarter Start
        
        title_text = 'Books Completed'

        if books_finished.empty and not year:
            if year:
                 pass
            else:
                return None
            
        # 3. Resample by Time AND Format
        # We need to set index to finish_date
        books_finished.set_index('finish_date', inplace=True)
        
        # Helper for titles
        def get_titles(series):
            return '<br>'.join([f"• {t}" for t in series])
        
        # We need to group by format as well for resampling.
        # But resample is time-based. We can group by [pd.Grouper(freq=freq), 'format']
        resampled = books_finished.groupby([pd.Grouper(freq=freq), 'format']).agg({
            'title': ['count', get_titles]
        })
        
        # Flatten columns
        resampled.columns = ['count', 'titles_list']
        resampled = resampled.reset_index()
        
        # Force Full Range if Year is selected (for all formats? logic gets complex with stacking)
        # If we reindex, we lose the format-grouping structure unless we do it per format or cross join.
        # Simpler approach: Just plot what exists. If a month has 0 books, it won't show a bar.
        # If user explicitly wants empty months, we can reindex the time column specifically.
        
        # Prepare X-Axis Column
        x_col = 'finish_date'
        if not year:
            # Custom Quarter Labels: "2025 Q1"
            resampled['quarter_label'] = resampled['finish_date'].apply(lambda d: f"{d.year} Q{d.quarter}")
            x_col = 'quarter_label'
        
        # 4. Plot (Stacked Bar)
        fig = px.bar(
            resampled,
            x=x_col,
            y='count',
            color='format',
            title=title_text,
            labels={'finish_date': 'Date', 'quarter_label': 'Quarter', 'count': 'Books Completed', 'format': 'Format'},
            custom_data=['titles_list'],
            color_discrete_map=self.FORMAT_COLORS
        )
        
        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            title_x=0.5,
            title_xanchor='center',
            title_y=0.95,
            xaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=False
            ),
            yaxis=dict(
                gridcolor=self.THEME_COLORS['grid'],
                showgrid=True,
                dtick=1 # Ensure integer ticks
            ),
            bargap=0.2,
        )
        
        # Update Bars & Format
        hover_template = "<b>%{x}</b><br>Count: %{y}<br><br>%{customdata[0]}<extra></extra>"
        if year:
            # Yearly View: Date Axis
            fig.update_xaxes(dtick="M1", tickformat="%b")
            fig.update_traces(hovertemplate="<b>%{x|%B %Y}</b><br>Count: %{y}<br><br>%{customdata[0]}<extra></extra>")
        else:
            # All Time View: Categorical Quarter Strings
            fig.update_xaxes(type='category')
            fig.update_traces(hovertemplate="<b>%{x}</b><br>Count: %{y}<br><br>%{customdata[0]}<extra></extra>")
        
        fig.update_traces(
            marker_line_width=0,
            hoverlabel=dict(bgcolor="black")
        )
            
        return fig

    def plot_reading_patterns(self, year: int = None):
        """
        Analysis of Reading Patterns (Stacked by Format).
        Subplot 1: Daily Reading Pattern (Avg minutes read on a given weekday, split by format).
        Subplot 2: Monthly Reading Pattern (Avg/Total minutes read in a month, split by format).
        """
        df = self.data.copy()
        
        # Filter by year if needed
        if year:
            df = df[df['year'] == year]
            title = 'Reading Habits' 
        else:
            title = 'Reading Habits'

        if df.empty:
            return None
            
        # Ensure format column exists
        if 'format' not in df.columns:
            df['format'] = 'kindle'

        # Determine full date range for normalization
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        # If showing a specific year, ensure we cover the full year (or up to today if current year)
        # Actually, best to just use the min/max from data or force full year range if 'year' is set?
        # Let's stick to the data range to avoid skewing defined periods, 
        # BUT for "Average" to be meaningful "Per Weekday", we need the count of weekdays in that range.
        
        if year:
            # Force full year for correct month counts (12 months)
            # But for weekdays, we use the actual range of the year
            # min_date = pd.Timestamp(f"{year}-01-01")
            # max_date = pd.Timestamp(f"{year}-12-31")
            # However, if data only exists for Jan-Feb, dividing by 52 Mondays would be wrong.
            # So using data range is safer.
            pass
            
        full_date_range = pd.date_range(start=min_date, end=max_date)
        
        # 1. Prepare Daily Data (Total minutes per day and format)
        daily = df.groupby(['date', 'format'])['duration'].sum().reset_index()
        daily['minutes'] = daily['duration'] / 60
        daily['hours'] = daily['duration'] / 3600
        daily['date'] = pd.to_datetime(daily['date'])
        daily['day_of_week'] = daily['date'].dt.dayofweek
        daily['month'] = daily['date'].dt.month
        
        # --- Subplot 1: Daily Pattern (True Average Minutes per Weekday by Format) ---
        # Calculate how many of each weekday exist in the full range
        weekday_counts = full_date_range.dayofweek.value_counts().sort_index()
        # weekday_counts is Series: index 0-6, value = count
        
        # Sum duration per [day_of_week, format]
        # Exclude paperback for daily pattern as synthetic data flattens the distribution
        weekday_sums = daily[daily['format'] != 'paperback'].groupby(['day_of_week', 'format'])['minutes'].sum().reset_index()
        
        # Normalize
        def normalize_weekday(row):
            count = weekday_counts.get(row['day_of_week'], 1)
            return row['minutes'] / count if count > 0 else 0
            
        weekday_sums['avg_minutes'] = weekday_sums.apply(normalize_weekday, axis=1)
        
        days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        weekday_sums['Day'] = weekday_sums['day_of_week'].map(days_map)
        
        import calendar
        
        # --- Subplot 2: Monthly Reading Pattern ---
        if year:
            # Single Year: Absolute Hours per Month by Format
            monthly_data = daily.groupby(['month', 'format'])['duration'].sum().reset_index()
            # Use minutes for formatting
            monthly_data['minutes'] = monthly_data['duration'] / 60
            monthly_data['hours'] = monthly_data['duration'] / 3600
            
            monthly_data['formatted_time'] = monthly_data['minutes'].apply(
                lambda x: f"{int(x // 60)}h {int(x % 60)}m"
            )
            
            y_col = 'hours'
            y_label_month = 'Total Time'
            hover_template_month = "<b>%{x}</b><br>Format: FMT_NAME<br>Total: %{customdata[0]}<extra></extra>"
        else:
            # All Time: Average Hours per Month by Format
            
            # Count occurrences of each month in full range
            month_counts = full_date_range.month.value_counts().sort_index()
            
            # Sum per [month, format]
            monthly_sums = daily.groupby(['month', 'format'])['hours'].sum().reset_index()
            
            # Normalize
            def normalize_month(row):
                count = month_counts.get(row['month'], 1)
                return row['hours'] / count if count > 0 else 0
                
            monthly_sums['avg_hours'] = monthly_sums.apply(normalize_month, axis=1)
            
            # Formatted time for Avg
            monthly_sums['avg_minutes'] = monthly_sums['avg_hours'] * 60
            monthly_sums['formatted_time'] = monthly_sums['avg_minutes'].apply(
                lambda x: f"{int(x // 60)}h {int(x % 60)}m"
            )
            
            monthly_data = monthly_sums
            
            y_col = 'avg_hours'
            y_label_month = 'Avg Time'
            hover_template_month = "<b>%{x}</b><br>Format: FMT_NAME<br>Avg: %{customdata[0]}<extra></extra>"

        monthly_data['Month'] = monthly_data['month'].apply(lambda x: calendar.month_abbr[x])

        # Create Subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Daily Reading Pattern", f"Monthly Reading Pattern"),
            horizontal_spacing=0.15
        )
        
        # --- Trace 1: Weekday (Stacked by Format) ---
        format_order = ['ebook', 'paperback', 'audiobook']
        
        for fmt in format_order:
            # Filter for this format
            f_data = weekday_sums[weekday_sums['format'] == fmt]
            if f_data.empty:
                continue
                
            fig.add_trace(
                go.Bar(
                    x=f_data['Day'],
                    y=f_data['avg_minutes'],
                    name=fmt.title(),
                    marker_color=self.FORMAT_COLORS.get(fmt, self.THEME_COLORS['primary']),
                    hovertemplate="<b>%{x}</b><br>Format: " + fmt.title() + "<br>Avg: %{y:.0f} min<extra></extra>",
                    showlegend=False
                ),
                row=1, col=1
            )

        # --- Trace 2: Month (Stacked by Format) ---
        for fmt in format_order:
            # Filter
            m_data = monthly_data[monthly_data['format'] == fmt]
            if m_data.empty:
                continue
                
            fig.add_trace(
                go.Bar(
                    x=m_data['Month'],
                    y=m_data[y_col],
                    name=fmt.title(),
                    marker_color=self.FORMAT_COLORS.get(fmt, self.THEME_COLORS['accent']),
                    customdata=m_data[['formatted_time']].values, # Pass formatted time
                    hovertemplate=hover_template_month.replace("FMT_NAME", fmt.title()),
                    showlegend=True 
                ),
                row=1, col=2
            )
        
        # Merge legends
        names = set()
        for trace in fig.data:
            if trace.name in names:
                trace.showlegend = False
            else:
                names.add(trace.name)
                
        # Styling
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', y=0.95),
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            barmode='stack', # Enable Stacking
            yaxis=dict(title='Avg Minutes', gridcolor=self.THEME_COLORS['grid']),
            yaxis2=dict(title=y_label_month, gridcolor=self.THEME_COLORS['grid']),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Sort Month Axis
        fig.update_xaxes(
            categoryorder='array', 
            categoryarray=[calendar.month_abbr[i] for i in range(1, 13)],
            row=1, col=2
        )
        
        # Sort Weekday Axis (Mon-Sun)
        fig.update_xaxes(
            categoryorder='array',
            categoryarray=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            row=1, col=1
        )
        
        fig.update_traces(
            marker_line_width=0,
            hoverlabel=dict(bgcolor="black")
        )
        
        return fig

    def plot_language_stats(self, year: int = None, external_data: pd.DataFrame = None):
        """
        Donut chart (Yearly) or Stacked Area (All Time) for language distribution.
        Based on NUMBER OF BOOKS.
        """
        df = None
        
        # Prefer external data (Numbers) if available
        if external_data is not None and not external_data.empty:
            ext_df = external_data.copy()
            
            # Normalize column names: Use end_date as primary date, else start_date
            if 'end_date' in ext_df.columns and 'start_date' in ext_df.columns:
                ext_df['date'] = ext_df['end_date'].combine_first(ext_df['start_date'])
            elif 'end_date' in ext_df.columns:
                ext_df['date'] = ext_df['end_date']
            elif 'start_date' in ext_df.columns:
                ext_df['date'] = ext_df['start_date']
                
            # Create year column if missing
            if 'year' not in ext_df.columns and 'date' in ext_df.columns:
                ext_df['date'] = pd.to_datetime(ext_df['date'])
                ext_df['year'] = ext_df['date'].dt.year

            # Check for language column or rename 'lingua'
            if 'language' in ext_df.columns:
                df = ext_df
            elif 'lingua' in ext_df.columns:
                ext_df['language'] = ext_df['lingua']
                df = ext_df
                
        # Fallback to internal data if external yielded no valid df (or missing language)
        if df is None:
            df = self.data.copy()
        
        # Ensure language column exists
        if 'language' not in df.columns:
            return None
            
        # Clean language codes if needed
        df['language'] = df['language'].fillna('other').astype(str).str.lower().str.strip()
        
        # Standardize language names for display
        lang_map = {
            'en': 'English', 'english': 'English',
            'it': 'Italian', 'italian': 'Italian',
            'ja': 'Japanese', 'japanese': 'Japanese',
            'fr': 'French', 'french': 'French',
            'es': 'Spanish', 'spanish': 'Spanish',
            'de': 'German', 'german': 'German',
            'ru': 'Russian', 'russian': 'Russian',
            'zh': 'Chinese', 'chinese': 'Chinese'
        }
        df['language_label'] = df['language'].map(lang_map).fillna(df['language'].str.title())
        
        if year:
            # --- Yearly View: Donut Chart ---
            df = df[df['year'] == year]
            if df.empty: return None
            
            # Aggregate by language (Count unique books)
            count_col = 'id_book' if 'id_book' in df.columns else 'title'
            lang_stats = df.groupby('language_label')[count_col].nunique().reset_index()
            lang_stats.rename(columns={count_col: 'count'}, inplace=True)
            
            total_books = lang_stats['count'].sum()
            if total_books == 0: return None
            
            lang_stats['percentage'] = lang_stats['count'] / total_books
            
            fig = px.pie(
                lang_stats, 
                values='count', 
                names='language_label',
                title=f'Books Read by Language in {year}',
                hole=0.4, # Donut
                color='language_label',
                color_discrete_map=self.LANGUAGE_COLORS
            )
            
            fig.update_layout(
                paper_bgcolor=self.THEME_COLORS['paper'],
                plot_bgcolor=self.THEME_COLORS['background'],
                font_color=self.THEME_COLORS['text'],
                title_x=0.5,
                title_xanchor='center',
                width=self.PLOT_WIDTH,
                height=500, 
                margin=dict(t=80, l=50, r=50, b=50),
                showlegend=True
            )
            
            fig.update_traces(
                textinfo='percent+label',
                textfont_size=14,
                hovertemplate="<b>%{label}</b><br>Books: <b>%{value}</b><br>Share: <b>%{percent:.1%}</b><extra></extra>",
                texttemplate="%{percent:.1%} %{label}",
                marker=dict(line=dict(color=self.THEME_COLORS['background'], width=2))
            )
            
            return fig
            
        else:
            # --- All Time View: 100% Stacked Area ---
            # Aggregate by Year and Language (Count unique books)
            if 'start_datetime' in df.columns:
                df['year_dt'] = df['start_datetime'].dt.to_period('Y').dt.start_time
            elif 'date' in df.columns:
                df['start_datetime'] = pd.to_datetime(df['date'])
                df['year_dt'] = df['start_datetime'].dt.to_period('Y').dt.start_time
            else:
                return None
            
            # Group by year and language, counting unique books
            count_col = 'id_book' if 'id_book' in df.columns else 'title'
            yearly = df.groupby(['year_dt', 'language_label'])[count_col].nunique().reset_index()
            yearly.rename(columns={count_col: 'count'}, inplace=True)
            
            if yearly.empty: return None
            
            fig = px.area(
                yearly, 
                x='year_dt', 
                y='count', 
                color='language_label',
                groupnorm='percent', # Creates the 100% Stacked Area
                title='Language Distribution Over Time (Books Read)',
                labels={'count': 'Books', 'year_dt': 'Year', 'language_label': 'Language'},
                color_discrete_map=self.LANGUAGE_COLORS
            )
            
            fig.update_layout(
                paper_bgcolor=self.THEME_COLORS['paper'],
                plot_bgcolor=self.THEME_COLORS['background'],
                font_color=self.THEME_COLORS['text'],
                title_x=0.5,
                title_xanchor='center',
                width=self.PLOT_WIDTH,
                height=self.PLOT_HEIGHT,
                margin=dict(t=80, l=50, r=50, b=50),
                yaxis=dict(
                    ticksuffix='%', 
                    range=[0, 100],
                    gridcolor=self.THEME_COLORS['grid'],
                    title="Share of Books"
                ),
                xaxis=dict(
                    gridcolor=self.THEME_COLORS['grid'],
                    title=None
                ),
                hovermode='x unified'
            )
            
            fig.update_traces(
                line=dict(width=0),
                hovertemplate="<b>%{y}</b> books<extra></extra>", # Shows count in unified text
                hoverlabel=dict(bgcolor="black")
            )
            
            return fig

    def plot_acquisition_ratio(self, year: int = None, external_data: pd.DataFrame = None):
        """
        Donut Chart (Yearly) or Stacked Area (All Time) comparing Books Read vs Books Acquired.
        If external_data is provided (from Numbers), it is used as the exclusive source.
        """
        
        if external_data is not None and not external_data.empty:
            # --- USE EXTERNAL DATA SOURCE (NUMBERS) ---
            df = external_data.copy()
            
            # 1. Calculate Books Read (Finished)
            # Logic: Has a valid end_date
            if 'end_date' in df.columns:
                books_read = df.dropna(subset=['end_date']).copy()
                books_read['date'] = books_read['end_date']
                books_read['type'] = 'Read'
            else:
                books_read = pd.DataFrame(columns=['date', 'type'])

            # 2. Calculate Books Acquired
            # Logic: Purchase Date -> Start Date (if Sub/Borrowed) -> NaT
            books_acquired = df.copy()
            
            def get_acq_date_ext(row):
                # Priority 1: Purchase Date
                if 'purchase_date' in row and pd.notna(row['purchase_date']):
                    return row['purchase_date']
                
                # Priority 2: Start Date if Subscription/Borrowed
                ownership = str(row.get('ownership', '')).strip().lower()
                if ownership in ['subscription', 'borrowed']:
                    if 'start_date' in row and pd.notna(row['start_date']):
                        return row['start_date']
                        
                return pd.NaT

            def get_acq_type_ext(row):
                ownership = str(row.get('ownership', '')).strip().lower()
                if ownership in ['subscription', 'borrowed']:
                    return ownership.title()
                return 'Purchased'

            books_acquired['date'] = books_acquired.apply(get_acq_date_ext, axis=1)
            books_acquired['type'] = books_acquired.apply(get_acq_type_ext, axis=1)
            books_acquired = books_acquired.dropna(subset=['date'])

            # Labels are already 'Purchased', 'Subscription', 'Borrowed' from helper above.
            # No need to map them to 'Books ...'

        else:
            # --- USE INTERNAL DATA SOURCE (KINDLE + MERGED) ---
            df = self.data.copy()
            
            # 1. Calculate Books Read (Finished)
            # Filter for completed books
            if 'is_completed' in df.columns:
                read_df = df[df['is_completed'] == True]
            else:
                read_df = df
                
            # Get unique finished books with date
            books_read = read_df.groupby('id_book').agg({
                'start_datetime': 'max',
                'title': 'first'
            }).reset_index()
            books_read.rename(columns={'start_datetime': 'date'}, inplace=True)
            books_read['type'] = 'Read'
            
            # 2. Calculate Books Acquired (Purchased / Subscription / Borrowed)
            # We need purchase_date and ownership (if available) from df.
            cols_to_agg = {'title': 'first', 'start_datetime': 'min'}
            if 'purchase_date' in df.columns:
                cols_to_agg['purchase_date'] = 'first'
            if 'ownership' in df.columns:
                cols_to_agg['ownership'] = 'first'
                
            books_acquired = df.groupby('id_book').agg(cols_to_agg).reset_index()
            
            # Logic to determine acquisition date and type
            def get_acquisition_date(row):
                # If explicit purchase date, use it
                if 'purchase_date' in row and pd.notna(row['purchase_date']):
                    return row['purchase_date']
                
                # Check ownership case-insensitive
                ownership = str(row.get('ownership', '')).strip().lower()
                if 'ownership' in row and ownership in ['subscription', 'borrowed']:
                    return row['start_datetime']
                return pd.NaT

            def get_acquisition_type(row):
                ownership = str(row.get('ownership', '')).strip().lower()
                if 'ownership' in row and ownership in ['subscription', 'borrowed']:
                    return ownership.title() # Return Title Case for display
                # Default to Purchased
                return 'Purchased'

            books_acquired['date'] = books_acquired.apply(get_acquisition_date, axis=1)
            books_acquired['type'] = books_acquired.apply(get_acquisition_type, axis=1)
            
            # Filter only those with valid date
            books_acquired = books_acquired.dropna(subset=['date'])
        
        # We need to distinguish "Books Purchased" from "Books Subscription" etc in the chart labels
        # Standardize type names for the legend
        # Standardize type names for the legend
        # "Purchased" -> "Purchased"
        # "Subscription" -> "Subscription"
        # "Borrowed" -> "Borrowed"
        
        type_map = {
            'Purchased': 'Purchased',
            'Subscription': 'Subscription',
            'Borrowed': 'Borrowed'
        }
        books_acquired['type'] = books_acquired['type'].map(type_map).fillna('Purchased')
        
        # 3. Create Visualization
        if year:
            # --- Yearly View: Donut Chart ---
            # Filter for current year
            this_year_read = books_read[books_read['date'].dt.year == year]
            this_year_acquired = books_acquired[books_acquired['date'].dt.year == year]
            
            if this_year_read.empty and this_year_acquired.empty:
                return None
                
            # Group Acquired by Type
            acquired_stats = this_year_acquired['type'].value_counts().reset_index()
            acquired_stats.columns = ['type', 'count']
            
            # Add Read count
            read_count = len(this_year_read)
            stats = pd.concat([
                pd.DataFrame([{'type': 'Read', 'count': read_count}]),
                acquired_stats
            ], ignore_index=True)
            
            # Filter out zero counts
            stats = stats[stats['count'] > 0]
            
            fig = px.pie(
                stats, 
                values='count', 
                names='type',
                title=f'Acquisition vs Reading in {year}',
                hole=0.4,
                color='type',
                color_discrete_map={
                    'Read': self.THEME_COLORS['secondary'],           # Green
                    'Purchased': self.THEME_COLORS['accent'],         # Yellow
                    'Subscription': '#8338ec',                        # Purple
                    'Borrowed': '#3a86ff'                             # Blue
                }
            )
            
            fig.update_layout(
                paper_bgcolor=self.THEME_COLORS['paper'],
                plot_bgcolor=self.THEME_COLORS['background'],
                font_color=self.THEME_COLORS['text'],
                title_x=0.5,
                title_xanchor='center',
                width=self.PLOT_WIDTH,
                height=500, 
                margin=dict(t=80, l=50, r=50, b=50),
                showlegend=True
            )
            
            # Central Text (Ratio) - Removed to match Language Stats style
            # ratio = (read_count / acquired_count * 100) if acquired_count > 0 else 0
            
            # fig.add_annotation(
            #     text=f"{ratio:.0f}%<br>Read",
            #     x=0.5, y=0.5,
            #     font_size=24,
            #     showarrow=False,
            #     font_color=self.THEME_COLORS['text']
            # )
            
            fig.update_traces(
                textinfo='percent+label',
                textfont_size=14,
                hovertemplate="<b>%{label}</b><br>Count: <b>%{value}</b><br>Share: <b>%{percent:.1%}</b><extra></extra>",
                texttemplate="%{percent:.1%} %{label}",
                marker=dict(line=dict(color=self.THEME_COLORS['background'], width=2))
            )
            
            return fig
            
        else:
            # --- All Time View: 100% Stacked Area ---
            # Aggregate by Year
            
            # Combine datasets for unified processing
            books_read['year'] = books_read['date'].dt.year
            books_acquired['year'] = books_acquired['date'].dt.year
            
            read_yearly = books_read.groupby('year').size().reset_index(name='count')
            read_yearly['type'] = 'Read'
            
            # Group acquired by year AND type
            books_acquired['year'] = books_acquired['date'].dt.year
            acquired_yearly = books_acquired.groupby(['year', 'type']).size().reset_index(name='count')
            
            combined = pd.concat([read_yearly, acquired_yearly])
            
            # Ensure we cover all years range
            if combined.empty:
                 return None
                 
            min_year = combined['year'].min()
            max_year = combined['year'].max()
            
            if pd.isna(min_year) or pd.isna(max_year):
                return None
               
            # Create full grid of Year x Type
            all_years = range(int(min_year), int(max_year) + 1)
            all_types = combined['type'].unique()
            
            import itertools
            grid = pd.DataFrame(list(itertools.product(all_years, all_types)), columns=['year', 'type'])
            
            # Merge actual data into grid
            final_df = grid.merge(combined, on=['year', 'type'], how='left').fillna({'count': 0})
            final_df['year_date'] = pd.to_datetime(final_df['year'], format='%Y')

            # Create Stacked Area (100% normalized to show ratio evolution)
            # User asked for "Area for All Years", usually implies stacked volume, 
            # BUT "Same style as language" which is 100% stacked.
            # "Rapporto tra libri comprati... e letti" -> Ratio. 
            # So 100% Stacked Area is best to visualize the ratio.
            
            fig = px.area(
                final_df, 
                x='year_date', 
                y='count', 
                color='type',
                groupnorm='percent', # 100% Stacked
                title='Acquisition vs reading Ratio Over Time',
                labels={'count': 'Books', 'year_date': 'Year', 'type': 'Category'},
                color_discrete_map={
                    'Read': self.THEME_COLORS['secondary'],
                    'Purchased': self.THEME_COLORS['accent'],
                    'Subscription': '#8338ec',
                    'Borrowed': '#3a86ff'
                }
            )
            
            fig.update_layout(
                paper_bgcolor=self.THEME_COLORS['paper'],
                plot_bgcolor=self.THEME_COLORS['background'],
                font_color=self.THEME_COLORS['text'],
                title_x=0.5,
                title_xanchor='center',
                width=self.PLOT_WIDTH,
                height=self.PLOT_HEIGHT,
                margin=dict(t=80, l=50, r=50, b=50),
                yaxis=dict(
                    ticksuffix='%', 
                    range=[0, 100],
                    gridcolor=self.THEME_COLORS['grid'],
                    title="Share of Activity"
                ),
                xaxis=dict(
                    gridcolor=self.THEME_COLORS['grid'],
                    title=None
                ),
                hovermode='x unified'
            )
            
            fig.update_traces(
                line=dict(width=0),
                hovertemplate="<b>%{y}</b> books<extra></extra>",
                hoverlabel=dict(bgcolor="black")
            )
            
            return fig

    def plot_reading_speed_scatter(self, year: int = None, metric: str = 'hours'):
        """
        Scatter plot of Pages vs. Reading Time.
        metric: 'hours' (Reading Time) or 'days' (Days to Finish)
        """
        df = self.data.copy()
        
        # Filter logic based on metric
        if metric == 'hours':
            # Exclude Paperback
            if 'format' in df.columns:
                df = df[df['format'] != 'paperback']
            # Exclude Manual Ebooks (Numbers)
            if 'data_source' in df.columns:
                df = df[~((df['format'] == 'ebook') & (df['data_source'] == 'numbers'))]
                
        if year:
            # Filter for books that have at least some activity in this year
            books_in_year = df[df['year'] == year]['title'].unique()
            df = df[df['title'].isin(books_in_year)]
            
        # --- EXCLUDE AUDIOBOOKS ---
        # Exclude for 'hours' metric (Read Speed), but keep for 'days' (Days to Finish)
        if 'format' in df.columns and metric == 'hours':
            df = df[df['format'] != 'audiobook']
            
        # --- Filter for COMPLETED books only ---
        # 1. Identify completed books
        # Logic: 
        # - Ebook: Sum of pages_read >= 95% of total pages? 
        #   (Note: 'pages_read' is usually just '1' per row, need to sum)
        # - Paperback/Numbers: If they exist in Numbers/manual import, they are usually finished books unless explicit start/end
        
        # Calculate completion per book title
        # Group by title to get stats
        book_completion = df.groupby(['title', 'format']).agg({
            'pages_read': 'sum',
            'pages': 'max', # Total pages
            'duration': 'sum'
        }).reset_index()
        
        # Audiobooks should already have is_completed in df if processed correctly
        # But let's check if 'is_completed' col exists in df
        if 'is_completed' in df.columns:
            # Get max is_completed per book
            completed_flags = df.groupby('title')['is_completed'].any()
            book_completion['is_completed_flag'] = book_completion['title'].map(completed_flags).fillna(False)
        else:
            book_completion['is_completed_flag'] = False
            
        # Fix Audiobook Data for completion check
        mask_audio = (book_completion['format'] == 'audiobook')
        if mask_audio.any():
            # Estimate pages from duration if missing (1 min = 1 page)
            zero_pages = mask_audio & (book_completion['pages'] <= 0)
            if zero_pages.any():
                book_completion.loc[zero_pages, 'pages'] = book_completion.loc[zero_pages, 'duration'] / 60
            
            # Set pages_read from duration
            book_completion.loc[mask_audio, 'pages_read'] = book_completion.loc[mask_audio, 'duration'] / 60

        # Calculate for Ebooks/Paperbacks if flag is False
        # Ratio of Pages Read to Total Pages
        book_completion['read_ratio'] = book_completion['pages_read'] / book_completion['pages'].replace(0, 1)
        
        # Define Completed Logic
        def check_completed(row):
            if row['is_completed_flag']: return True
            
            fmt = str(row['format']).lower()
            
            # Paperbacks (Manual) - assumed done if imported?
            # Or check pages_read (which is = pages for manual entries)
            if fmt == 'paperback':
                return row['read_ratio'] >= 0.95
                
            # Ebooks (Kindle)
            # Threshold 90% to account for front/back matter
            if fmt == 'ebook':
                return row['read_ratio'] >= 0.90

            # Audiobooks
            if fmt == 'audiobook':
                return row['read_ratio'] >= 0.95
                
            return False

        book_completion['is_really_completed'] = book_completion.apply(check_completed, axis=1)
        
        completed_titles = book_completion[book_completion['is_really_completed']]['title'].unique()
        df = df[df['title'].isin(completed_titles)]

        title = f'Reading Speed: Pages vs. {"Reading Time" if metric == "hours" else "Days to Finish"}'
        
        if df.empty:
            return None

        # Group by Book
        # We need: Title, Total Pages (Metadata), Format, Total Duration, Start Date, End Date, Authors
        # Using Book ID is safer but let's stick to title for grouping to align with other plots
        
        book_stats = df.groupby(['title', 'format', 'authors']).agg({
            'pages': 'max',
            'duration': 'sum',
            'date': ['min', 'max']
        }).reset_index()
        
        # Flatten columns
        book_stats.columns = ['title', 'format', 'authors', 'pages', 'total_duration_sec', 'start_date', 'end_date']

        # Fix Pages for Audiobooks (if 0, estimate from duration)
        mask_audio_stats = (book_stats['format'] == 'audiobook') & (book_stats['pages'] <= 0)
        if mask_audio_stats.any():
            book_stats.loc[mask_audio_stats, 'pages'] = book_stats.loc[mask_audio_stats, 'total_duration_sec'] / 60
        
        # Calculate Metrics
        book_stats['hours'] = book_stats['total_duration_sec'] / 3600
        book_stats['days'] = (pd.to_datetime(book_stats['end_date']) - pd.to_datetime(book_stats['start_date'])).dt.days + 1
        
        # Filter out books with 0 pages (Audiobooks often have 0 unless set)
        book_stats = book_stats[book_stats['pages'] > 0]
        
        # Filter noise
        book_stats = book_stats[book_stats['pages'] > 20] 
        book_stats = book_stats[book_stats['hours'] > 1]
        
        if book_stats.empty:
            return None
            
        if book_stats.empty:
            return None
            
        x_col = 'hours' if metric == 'hours' else 'days' # X is now Time
        x_label = 'Reading Time (Hours)' if metric == 'hours' else 'Days to Finish'
        
        # Calculate GLOBAL Average Speed (Total Pages / Total Time)
        total_pages = book_stats['pages'].sum()
        total_time = book_stats[x_col].sum()
        avg_speed = total_pages / total_time if total_time > 0 else 0
        
        avg_label = f"{avg_speed:.1f} pages/hr" if metric == 'hours' else f"{avg_speed:.1f} pages/day"
        
        # Tooltip formatting
        book_stats['speed_label'] = book_stats.apply(
            lambda x: f"{x['pages'] / x['hours']:.1f} pages/hr" if metric == 'hours' and x['hours'] > 0 else 
                      f"{x['pages'] / x['days']:.1f} pages/day" if x['days'] > 0 else "N/A",
            axis=1
        )
        
        fig = px.scatter(
            book_stats,
            x=x_col, # Time on X
            y='pages', # Pages on Y
            color='format',
            title=title,
            labels={'pages': 'Total Pages', x_col: x_label, 'format': 'Format'},
            hover_name='title',
            custom_data=['speed_label', 'authors'],
            color_discrete_map=self.FORMAT_COLORS
        )
        
        # Add AVERAGE SPEED Reference Line (Through Origin)
        # Line equation: y = avg_speed * x
        if total_time > 0:
            max_x = book_stats[x_col].max()
            max_y_expected = max_x * avg_speed
            
            fig.add_trace(
                go.Scatter(
                    x=[0, max_x],
                    y=[0, max_y_expected],
                    mode='lines',
                    line=dict(color=self.THEME_COLORS['subtext'], width=2, dash='dash'),
                    name=f'Avg: {avg_label}',
                    hoverinfo='skip'
                )
            )
        
        # Trendline Removed (Replaced by Average Speed Line)


        fig.update_layout(
            paper_bgcolor=self.THEME_COLORS['paper'],
            plot_bgcolor=self.THEME_COLORS['background'],
            font_color=self.THEME_COLORS['text'],
            width=self.PLOT_WIDTH,
            height=self.PLOT_HEIGHT,
            margin=dict(t=80, l=50, r=50, b=50),
            title_x=0.5,
            xaxis=dict(gridcolor=self.THEME_COLORS['grid'], title=x_label, rangemode='tozero'),
            yaxis=dict(gridcolor=self.THEME_COLORS['grid'], title='Book Length (Pages)', rangemode='tozero'),
            showlegend=True
        )
        
        fig.update_traces(
            marker=dict(size=12, line=dict(width=1, color=self.THEME_COLORS['background'])),
            hovertemplate="<b>%{hovertext}</b><br><i>%{customdata[1]}</i><br><br>" + x_label + ": %{x:.1f}<br>Pages: %{y}<br>Speed: %{customdata[0]}<extra></extra>"
        )
        
        return fig
