"""Data processing and storage for Whoop and lab data."""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import config


class HealthDataProcessor:
    """Process and combine Whoop data with lab test results."""
    
    def __init__(self):
        self.output_dir = config.DATA_OUTPUT_DIR
    
    def process_whoop_recovery(self, recovery_data: List[Dict]) -> pd.DataFrame:
        """
        Process Whoop recovery data into a pandas DataFrame.
        
        Args:
            recovery_data: List of recovery records from Whoop API
            
        Returns:
            DataFrame with daily recovery metrics
        """
        if not recovery_data:
            return pd.DataFrame()
        
        processed = []
        for record in recovery_data:
            score = record.get('score', {})
            
            # Extract date from cycle_id or created_at
            date = None
            if 'created_at' in record:
                date = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00')).date()
            
            processed.append({
                'date': date,
                'cycle_id': record.get('cycle_id'),
                'recovery_score': score.get('recovery_score'),
                'hrv_rmssd': score.get('hrv_rmssd_milli'),
                'resting_hr': score.get('resting_heart_rate'),
                'spo2': score.get('spo2_percentage'),
                'skin_temp': score.get('skin_temp_celsius'),
                'score_state': record.get('score_state'),
                'user_calibrating': record.get('user_calibrating', False)
            })
        
        df = pd.DataFrame(processed)
        if not df.empty and 'date' in df.columns:
            df = df.sort_values('date')
        return df
    
    def process_whoop_sleep(self, sleep_data: List[Dict]) -> pd.DataFrame:
        """
        Process Whoop sleep data into a pandas DataFrame.
        
        Args:
            sleep_data: List of sleep records from Whoop API
            
        Returns:
            DataFrame with sleep metrics
        """
        if not sleep_data:
            return pd.DataFrame()
        
        processed = []
        for record in sleep_data:
            score = record.get('score', {})
            stage_summary = score.get('stage_summary', {})
            
            # Extract date from end time
            date = None
            if 'end' in record:
                date = datetime.fromisoformat(record['end'].replace('Z', '+00:00')).date()
            
            # Convert milliseconds to hours
            ms_to_hours = 1000 * 60 * 60
            
            processed.append({
                'date': date,
                'sleep_id': record.get('id'),
                'sleep_performance': score.get('sleep_performance_percentage'),
                'sleep_efficiency': score.get('sleep_efficiency_percentage'),
                'sleep_consistency': score.get('sleep_consistency_percentage'),
                'total_sleep_hours': stage_summary.get('total_in_bed_time_milli', 0) / ms_to_hours,
                'light_sleep_hours': stage_summary.get('total_light_sleep_time_milli', 0) / ms_to_hours,
                'deep_sleep_hours': stage_summary.get('total_slow_wave_sleep_time_milli', 0) / ms_to_hours,
                'rem_sleep_hours': stage_summary.get('total_rem_sleep_time_milli', 0) / ms_to_hours,
                'awake_hours': stage_summary.get('total_awake_time_milli', 0) / ms_to_hours,
                'respiratory_rate': score.get('respiratory_rate'),
                'disturbance_count': score.get('disturbance_count'),
                'sleep_cycle_count': score.get('sleep_cycle_count')
            })
        
        df = pd.DataFrame(processed)
        if not df.empty and 'date' in df.columns:
            df = df.sort_values('date')
        return df
    
    def process_whoop_cycles(self, cycle_data: List[Dict]) -> pd.DataFrame:
        """
        Process Whoop cycle (day) data into a pandas DataFrame.
        
        Args:
            cycle_data: List of cycle records from Whoop API
            
        Returns:
            DataFrame with daily strain and activity metrics
        """
        if not cycle_data:
            return pd.DataFrame()
        
        processed = []
        for record in cycle_data:
            score = record.get('score', {})
            
            # Extract date from start time
            date = None
            if 'start' in record:
                date = datetime.fromisoformat(record['start'].replace('Z', '+00:00')).date()
            
            processed.append({
                'date': date,
                'cycle_id': record.get('id'),
                'day_strain': score.get('strain'),
                'avg_hr': score.get('average_heart_rate'),
                'max_hr': score.get('max_heart_rate'),
                'kilojoules': score.get('kilojoule')
            })
        
        df = pd.DataFrame(processed)
        if not df.empty and 'date' in df.columns:
            df = df.sort_values('date')
        return df
    
    def process_whoop_workouts(self, workout_data: List[Dict]) -> pd.DataFrame:
        """
        Process Whoop workout data into a pandas DataFrame.
        
        Args:
            workout_data: List of workout records from Whoop API
            
        Returns:
            DataFrame with workout metrics
        """
        if not workout_data:
            return pd.DataFrame()
        
        processed = []
        for record in workout_data:
            score = record.get('score', {})
            
            # Extract date from start time
            date = None
            if 'start' in record:
                date = datetime.fromisoformat(record['start'].replace('Z', '+00:00')).date()
            
            processed.append({
                'date': date,
                'workout_id': record.get('id'),
                'sport': record.get('sport_name'),
                'workout_strain': score.get('strain'),
                'avg_hr': score.get('average_heart_rate'),
                'max_hr': score.get('max_heart_rate'),
                'kilojoules': score.get('kilojoule'),
                'distance_meters': score.get('distance_meter')
            })
        
        df = pd.DataFrame(processed)
        if not df.empty and 'date' in df.columns:
            df = df.sort_values('date')
        return df
    
    def process_lab_data(self, lab_results: List[Dict]) -> pd.DataFrame:
        """
        Process lab test results into a pandas DataFrame.
        
        Args:
            lab_results: List of parsed lab result dictionaries
            
        Returns:
            DataFrame with lab test values
        """
        if not lab_results:
            return pd.DataFrame()
        
        all_tests = []
        for lab_record in lab_results:
            test_date = lab_record.get('test_date')
            test_type = lab_record.get('test_type')
            
            for result in lab_record.get('results', []):
                all_tests.append({
                    'date': test_date,
                    'test_type': test_type,
                    'test_name': result.get('test_name'),
                    'value': result.get('value'),
                    'unit': result.get('unit'),
                    'reference_range': result.get('reference_range')
                })
        
        df = pd.DataFrame(all_tests)
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
            df = df.sort_values('date')
        return df
    
    def combine_daily_metrics(self, recovery_df: pd.DataFrame, sleep_df: pd.DataFrame, 
                              cycles_df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine Whoop data into a single daily metrics DataFrame.
        
        Args:
            recovery_df: Recovery data
            sleep_df: Sleep data
            cycles_df: Cycle data
            
        Returns:
            Combined DataFrame with all daily metrics
        """
        # Start with date range
        start = datetime.strptime(config.DATA_START_DATE, '%Y-%m-%d').date()
        end = datetime.strptime(config.DATA_END_DATE, '%Y-%m-%d').date()
        
        date_range = pd.date_range(start=start, end=end, freq='D')
        daily_df = pd.DataFrame({'date': [d.date() for d in date_range]})
        
        # Merge recovery data
        if not recovery_df.empty:
            daily_df = daily_df.merge(recovery_df, on='date', how='left')
        
        # Merge sleep data
        if not sleep_df.empty:
            daily_df = daily_df.merge(sleep_df, on='date', how='left', suffixes=('', '_sleep'))
        
        # Merge cycle data
        if not cycles_df.empty:
            daily_df = daily_df.merge(cycles_df, on='date', how='left', suffixes=('', '_cycle'))
        
        # Add event markers
        daily_df['event'] = ''
        for event in config.CRITICAL_EVENTS:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
            daily_df.loc[daily_df['date'] == event_date, 'event'] = event['name']
        
        return daily_df
    
    def save_data(self, data: Dict, filename: str):
        """
        Save processed data to JSON file.
        
        Args:
            data: Data to save
            filename: Output filename
        """
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✓ Saved data to {output_path}")
    
    def save_dataframe(self, df: pd.DataFrame, filename: str):
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
        """
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"✓ Saved DataFrame to {output_path}")
