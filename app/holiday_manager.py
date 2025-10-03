import pandas as pd
from datetime import datetime
import os

def load_holidays_from_csv(csv_path):
    """Load holidays from CSV file"""
    try:
        holidays_df = pd.read_csv(csv_path)
        holidays_df.columns = holidays_df.columns.str.lower()
        
        # Validate required columns
        if 'date' not in holidays_df.columns:
            raise ValueError("Holiday CSV must have 'date' column")
        
        # Convert dates to standard format
        holiday_dates = []
        for _, row in holidays_df.iterrows():
            try:
                date_str = str(row['date'])
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        holiday_dates.append(date_obj.strftime('%Y-%m-%d'))
                        break
                    except ValueError:
                        continue
            except:
                continue
        
        return holiday_dates
    except Exception as e:
        print(f"Error loading holidays from CSV: {e}")
        return []

def get_default_holidays():
    """Get default Bangladesh holidays for 2024-2025"""
    return [
        '2024-02-21',  # International Mother Language Day
        '2024-03-17',  # Sheikh Mujibur Rahman's Birthday
        '2024-03-26',  # Independence Day
        '2024-04-14',  # Bengali New Year
        '2024-05-01',  # May Day
        '2024-08-15',  # National Mourning Day
        '2024-12-16',  # Victory Day
        '2024-12-25',  # Christmas Day
        '2025-02-21',  # International Mother Language Day
        '2025-03-17',  # Sheikh Mujibur Rahman's Birthday
        '2025-03-26',  # Independence Day
        '2025-04-14',  # Bengali New Year
        '2025-05-01',  # May Day
        '2025-08-15',  # National Mourning Day
        '2025-12-16',  # Victory Day
        '2025-12-25',  # Christmas Day
    ]

def load_holidays(csv_path=None):
    """Load holidays from CSV or use defaults"""
    if csv_path and os.path.exists(csv_path):
        holidays = load_holidays_from_csv(csv_path)
        if holidays:
            return holidays
    
    # Use default holidays if CSV not available or empty
    return get_default_holidays()

def filter_holidays_from_dates(exam_days, holidays):
    """Remove holiday dates from exam days list"""
    if not holidays:
        return exam_days
    
    # Convert holidays to set for faster lookup
    holiday_set = set(holidays)
    
    # Filter out holidays
    filtered_days = [day for day in exam_days if day not in holiday_set]
    
    return filtered_days

def is_holiday(date_str, holidays):
    """Check if a specific date is a holiday"""
    return date_str in holidays

if __name__ == "__main__":
    # Demo
    holidays = load_holidays()
    print(f"Loaded {len(holidays)} holidays:")
    for holiday in holidays[:5]:
        print(f"  {holiday}")
    
    # Test filtering
    test_dates = ['2024-03-26', '2024-03-27', '2024-03-28']
    filtered = filter_holidays_from_dates(test_dates, holidays)
    print(f"Original dates: {test_dates}")
    print(f"After filtering holidays: {filtered}")