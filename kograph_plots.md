# 📊 Kograph Dashboard - Plot Inventory

This document lists all available plots in the Kograph dashboard, detailing their visibility conditions and the types of reading data included.

| Plot Name | Function Name | Visibility Condition | Supported Formats | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Book Timeline** | `plot_book_timeline` | **Specific Year Only** | Ebook, Paperback, Audiobook | Shows reading sessions as a Gantt chart. Includes all data. |
| **Weekly Activity** | `plot_weekly_activity` | Always Visible | Ebook, Paperback, Audiobook | Stacked bar chart showing total hours per week by format. |
| **Time of Day** | `plot_time_of_day` | Always Visible | Ebook, Audiobook | Shows reading distribution across hours (0-23). **Excludes Paperback** (no timestamps). |
| **Reading Distribution** | `plot_reading_distribution` | Always Visible | Ebook, Audiobook | Histogram of daily reading minutes. **Excludes Paperback**. |
| **Reading Calendar** | `plot_reading_calendar` | **Specific Year Only** | Ebook, Audiobook | 3x4 Grid showing daily reading activity. **Excludes Paperback**. |
| **Reading Patterns (Daily)** | `plot_reading_patterns` (Subplot 1) | Always Visible | Ebook, Audiobook | Average minutes per weekday. **Excludes Paperback**. |
| **Reading Patterns (Monthly)** | `plot_reading_patterns` (Subplot 2) | Always Visible | Ebook, Paperback, Audiobook | Total minutes per month. **Includes Paperback**. |
| **Streak Histogram** | `plot_streaks` | Always Visible | Ebook, Audiobook | Distribution of reading streak lengths. **Excludes Paperback**. |
| **Streak Calendar** | `plot_streak_calendar` | **Specific Year Only** | Ebook, Audiobook | 3x4 Grid visualizing daily streak status. **Excludes Paperback**. |
| **Books Completed** | `plot_books_completed` | Always Visible | Ebook, Paperback, Audiobook | Count of books finished, aggregated by Month (Yearly) or Quarter (All Time). |
| **Language Stats** | `plot_language_stats` | Always Visible | Ebook, Paperback, Audiobook | Donut Chart (Yearly) or Stacked Area (All Time) based on book metadata. |
| **Cumulative Pages** | `plot_cumulative_pages` | Always Visible | Ebook, Paperback, Audiobook | Stacked area chart of total pages read. Audiobooks are converted (1 min = 1 page). |

## ⚠️ Missing or Hidden Plots

The following plots are referenced in `app.py` but appear to be missing or undefined in `src/visuals.py`, so they are currently not displayed:

*   `plot_country_distribution` (Library Insights)
*   `plot_purchase_timeline` (Library Insights)
