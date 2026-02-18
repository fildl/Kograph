# 📊 Kograph Dashboard - Plot Inventory
This document lists all available plots in the Kograph dashboard, detailing their visibility conditions and the types of reading data included.

| Plot Name | Function Name | Visibility Condition | Supported Formats | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Book Timeline** | `plot_book_timeline` | **Specific Year Only** | Ebook, Paperback, Audiobook | Shows reading sessions as a Gantt chart. Includes all data. |
| **Weekly Activity** | `plot_weekly_activity` | Always Visible | Ebook, Paperback, Audiobook | Stacked bar chart showing total hours per week by format. |
| **Time of Day** | `plot_time_of_day` | Always Visible | Ebook, Audiobook | Shows reading distribution across hours (0-23). **Excludes Paperback** (no timestamps). |
| **Reading Distribution** | `plot_reading_distribution` | Always Visible | Ebook, Audiobook | Histogram of daily reading minutes. **Aggregates formats**. Excludes Paperback. Shows **Mean/Median** lines. |
| **Reading Calendar** | `plot_reading_calendar` | **Specific Year Only** | Ebook, Audiobook | 3x4 Grid showing daily reading activity. **Excludes Paperback and Manual Ebooks**. |
| **Reading Patterns (Daily)** | `plot_reading_patterns` (Subplot 1) | Always Visible | Ebook, Audiobook | Average minutes per weekday. **Excludes Paperback**. |
| **Reading Patterns (Monthly)** | `plot_reading_patterns` (Subplot 2) | Always Visible | Ebook, Paperback, Audiobook | Total minutes per month. **Includes Paperback**. |
| **Streak Histogram** | `plot_streaks` | Always Visible | Ebook, Audiobook | Distribution of reading streak lengths. **Excludes Paperback and Manual Ebooks**. |
| **Streak Calendar** | `plot_streak_calendar` | **Specific Year Only** | Ebook, Audiobook | 3x4 Grid visualizing daily streak status. **Excludes Paperback and Manual Ebooks**. |
| **Books Completed** | `plot_books_completed` | Always Visible | Ebook, Paperback, Audiobook | Count of books finished, aggregated by Month (Yearly) or Quarter (All Time). |
| **Language Stats** | `plot_language_stats` | Always Visible | Ebook, Paperback, Audiobook | Donut Chart (Yearly) or Stacked Area (All Time) based on books read. |
| **Acquisition Ratio** | `plot_acquisition_ratio` | Always Visible | Ebook, Paperback, Audiobook | **Donut** (Yearly) or **100% Stacked Area** (All Time). Compares **Read** vs **Purchased**, **Subscription**, and **Borrowed**. Logic: Read $\ge$ 95%. |
| **Cumulative Pages** | `plot_cumulative_pages` | Always Visible | Ebook, Paperback, Audiobook | Stacked area chart of total pages read. Audiobooks are converted (1 min = 1 page). |
| **Reading Speed** | `plot_reading_speed_scatter` | Always Visible | Ebook, Paperback, Audiobook | Scatter Plot of Pages vs. Time. Metric toggle: **Hours** (Actual) or **Days**. |

## 🎨 Color Palette
The dashboard uses a specific color scheme to distinguish formats and data types:

*   🔴 **Ebook**: `#ef476f` (Primary)
*   🟢 **Audiobook**: `#06d6a0` (Secondary)
*   🟡 **Paperback**: `#ffd166` (Accent)
*   🔵 **Aggregated Data**: `#118ab2` (Grouped Stats)
*   📅 **Reading Calendar**: Gradient from `#2d3436` to `#ef476f`
*   🔥 **Reading Streaks**: Gradient from `#ffd166` to `#06d6a0`

## 📖 Book Completion Logic
A book is considered **"Completed"** based on the following criteria:
*   **Ebook (Kindle)**: Max page read is $\ge$ 95% of total pages.
*   **Audiobook**: Max progress time is $\ge$ 95% of total duration.
*   **Paperback/Manual**: If a "Finish Date" is present in the import file.


