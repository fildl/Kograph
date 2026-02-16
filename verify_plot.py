import pandas as pd
import sys
import os

# Add src to path
sys.path.append('src')

try:
    from visuals import ReadingVisuals
except ImportError:
    # Try alternate path if running from root
    sys.path.append('.')
    from src.visuals import ReadingVisuals

def verify_plot_reading_patterns():
    # Create dummy data
    data = {
        'date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'format': ['ebook'] * 50 + ['paperback'] * 50,
        'duration': [3600] * 100, # 1 hour each
        'year': [2023] * 100
    }
    df = pd.DataFrame(data)
    
    visuals = ReadingVisuals(df)
    
    print("Testing plot_reading_patterns()...")
    try:
        fig = visuals.plot_reading_patterns(year=2023)
        if fig:
            print("Successfully generated plot for year 2023")
            # Check if updated labels are present in layout
            # Note: Checking internal figure structure can be brittle, but let's see.
            # We expect yaxis2 title to be 'Total Hours'
            if 'Total Hours' in str(fig.layout.yaxis2.title.text):
                 print("SUCCESS: y-axis title updated to 'Total Hours'")
            else:
                 print(f"WARNING: y-axis title is '{fig.layout.yaxis2.title.text}' (Expected 'Total Hours')")
        else:
            print("Failed to generate plot (returned None)")
            
        fig_all_time = visuals.plot_reading_patterns(year=None)
        if fig_all_time:
            print("Successfully generated plot for All Time")
            # We expect yaxis2 title to be 'Avg Hours'
            if 'Avg Hours' in str(fig_all_time.layout.yaxis2.title.text):
                 print("SUCCESS: y-axis title updated to 'Avg Hours'")
            else:
                 print(f"WARNING: y-axis title is '{fig_all_time.layout.yaxis2.title.text}' (Expected 'Avg Hours')")

    except Exception as e:
        print(f"Error generating plot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_plot_reading_patterns()
