# 📊 Kograph Dashboard - Plot Inventory

This document lists all available plots in the Kograph dashboard, detailing their visibility conditions and the types of reading data included.

*   **Book Timeline** (`plot_book_timeline`)
    *   **Visibility**: Specific Year Only
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Shows reading sessions as a Gantt chart. Includes all reading data where start and finish dates are available.
    *   **Data Source**: All (Device Tracked + Manual Imports). Based on daily reading sessions.

*   **Weekly Activity** (`plot_weekly_activity`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Stacked bar chart showing total reading hours per week, split by format.
    *   **Data Source**: All (Device Tracked + Manual Imports). Uses `duration` field.

*   **Time of Day** (`plot_time_of_day`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Audiobook (Excludes Paperback)
    *   **Description**: Shows reading distribution across hours of the day (0-23). Excludes Paperback (no timestamps) and Manual Ebooks/Audiobooks.
    *   **Data Source**: Device Tracked Only (Kindle). Manual imports (Numbers) are excluded to avoid artificial 12:00 PM timestamps.

*   **Reading Distribution** (`plot_reading_distribution`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Audiobook (Excludes Paperback)
    *   **Description**: Histogram of daily reading minutes. Aggregates formats. Shows Mean/Median lines.
    *   **Data Source**: Mixed. Includes Device Tracked data and Manual Imports (if daily duration is available). Excludes Paperback.

*   **Reading Calendar** (`plot_reading_calendar`)
    *   **Visibility**: Specific Year Only
    *   **Formats**: Ebook, Audiobook (Device Tracked only)
    *   **Description**: 3x4 Grid showing daily reading activity heat map. Excludes Paperback and Manual Imports from Numbers.
    *   **Data Source**: Device Tracked Only (Kindle). Requires granular daily session data.

*   **Reading Patterns (Daily)** (`plot_reading_patterns`, Subplot 1)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Audiobook (Excludes Paperback)
    *   **Description**: Average minutes read per weekday.
    *   **Data Source**: Device Tracked + Manual Ebooks (if date available). Excludes Paperback.

*   **Reading Patterns (Monthly)** (`plot_reading_patterns`, Subplot 2)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Total minutes per month (Yearly) or Average per month (All Time). Includes Paperback.
    *   **Data Source**: All (Device Tracked + Manual Imports). Includes Paperback (synthetic duration if needed).

*   **Streak Histogram** (`plot_streaks`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Audiobook (Device Tracked only)
    *   **Description**: Distribution of reading streak lengths. Excludes Paperback and Manual Imports from Numbers.
    *   **Data Source**: Device Tracked Only (Kindle). Requires accurate daily streaks.

*   **Streak Calendar** (`plot_streak_calendar`)
    *   **Visibility**: Specific Year Only
    *   **Formats**: Ebook, Audiobook (Device Tracked only)
    *   **Description**: 3x4 Grid visualizing daily streak status. Excludes Paperback and Manual Imports from Numbers.
    *   **Data Source**: Device Tracked Only (Kindle).

*   **Books Completed** (`plot_books_completed`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Count of books finished, aggregated by Month (Yearly) or Quarter (All Time).
    *   **Data Source**: All (Device Tracked + Manual Imports). Based on book completion logic.

*   **Language Stats** (`plot_language_stats`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Donut Chart (Yearly) or 100% Stacked Area (All Time) showing distribution of books read by language.
    *   **Data Source**: Hybrid. Uses `readings.numbers` (External) if available to ensure accuracy, otherwise uses internal Metadata.

*   **Acquisition Ratio** (`plot_acquisition_ratio`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Donut (Yearly) or 100% Stacked Area (All Time). Compares Read books vs Purchased, Subscription, and Borrowed books. Ideally, Read should be $\ge$ 95%.
    *   **Data Source**: Hybrid. Uses `readings.numbers` (External) if available, otherwise merges internal Metadata + Purchase info.

*   **Cumulative Pages** (`plot_cumulative_pages`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook
    *   **Description**: Stacked area chart of cumulative pages read over time. Audiobooks are converted (1 min = 1 page).
    *   **Data Source**: All. Aggregates daily page progress. Audiobooks estimted from duration.

*   **Reading Speed** (`plot_reading_speed_scatter`)
    *   **Visibility**: Always Visible
    *   **Formats**: Ebook, Paperback, Audiobook (Days metric only)
    *   **Description**: Scatter Plot of Time vs. Pages. Includes a reference line for Average Speed. Metric toggle: **Hours** (Actual Reading Time, excludes Paperback/Manual Ebooks/Audiobooks) or **Days** (Days to Finish, includes Audiobooks).
    *   **Data Source**: 
        *   **Hours Metric**: Device Tracked Ebooks Only.
        *   **Days Metric**: All Formats (Paperback + Ebook + Audiobook).

## 🎨 Color Palette

The dashboard uses a specific color scheme to distinguish formats and data types:

*   🔴 **Ebook**: `#ef476f` (Primary)
*   🟢 **Audiobook**: `#06d6a0` (Secondary)
*   🟡 **Paperback**: `#ffd166` (Accent)
*   🔵 **Aggregated Data**: `#118ab2` (Grouped Stats)
*   📅 **Reading Calendar**: Gradient from `#2d3436` to `#ef476f`
*   🔥 **Reading Streaks**: Gradient from `#ffd166` to `#06d6a0`
*   🌈 **Book Timeline**: Cyclical palette of 10 vibrant spectral colors (Red to Purple).

## 📖 Book Completion Logic

A book is considered **"Completed"** based on the following criteria:

*   **Ebook (Kindle)**: Max page read is $\ge$ 90% of total pages.
*   **Audiobook**: Max progress time is $\ge$ 95% of total duration or marked as completed.
*   **Paperback/Manual**: If a "Finish Date" is present or marked as completed.
