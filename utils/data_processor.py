"""
Data processing utilities for the intrusion detection system.
This module handles the processing of network traffic data,
including feature extraction, normalization, and transformation.
"""

import pandas as pd
import numpy as np
import pickle
import os
import logging
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from io import StringIO

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_scaler(model_dir):
    """
    Load the feature scaler from disk.
    
    Args:
        model_dir (str): Directory containing the model files
        
    Returns:
        StandardScaler: Loaded scaler object
    """
    try:
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        logger.info(f"Scaler loaded successfully from {scaler_path}")
        return scaler
    except Exception as e:
        logger.error(f"Error loading scaler: {str(e)}")
        raise

def load_selected_features(model_dir):
    """
    Load the list of selected features for the model.
    
    Args:
        model_dir (str): Directory containing the model files
        
    Returns:
        list: List of feature names
    """
    try:
        features_path = os.path.join(model_dir, 'selected_features.csv')
        features = pd.read_csv(features_path, header=None)[0].tolist()
        logger.info(f"Selected features loaded successfully: {len(features)} features")
        return features
    except Exception as e:
        logger.error(f"Error loading selected features: {str(e)}")
        raise

def process_csv_file(file_path, selected_features, scaler):
    """
    Process a CSV file containing network traffic data.
    
    Args:
        file_path (str): Path to the CSV file
        selected_features (list): List of features to select
        scaler (StandardScaler): Scaler for feature normalization
        
    Returns:
        tuple: (processed_data, original_data)
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        logger.info(f"CSV file loaded successfully: {file_path}, {df.shape[0]} rows")
        
        # Validate features
        missing_features = [f for f in selected_features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Missing required features in CSV: {missing_features}")
        
        # Select required features
        X = df[selected_features]
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        logger.info(f"Data processed successfully: {X.shape[0]} rows, {X.shape[1]} features")
        return X_scaled, df
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}")
        raise

def process_csv_data(csv_data, selected_features, scaler):
    """
    Process CSV data from a string or bytes.
    
    Args:
        csv_data (str or bytes): CSV data
        selected_features (list): List of features to select
        scaler (StandardScaler): Scaler for feature normalization
        
    Returns:
        tuple: (processed_data, original_data)
    """
    try:
        # Parse CSV data
        df = pd.read_csv(StringIO(csv_data))
        logger.info(f"CSV data parsed successfully: {df.shape[0]} rows")
        
        # Validate features
        missing_features = [f for f in selected_features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Missing required features in CSV data: {missing_features}")
        
        # Select required features
        X = df[selected_features]
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        logger.info(f"Data processed successfully: {X.shape[0]} rows, {X.shape[1]} features")
        return X_scaled, df
    except Exception as e:
        logger.error(f"Error processing CSV data: {str(e)}")
        raise

def process_packet_data(packet_data, selected_features, scaler):
    """
    Process a single packet's data.
    
    Args:
        packet_data (dict): Dictionary with feature values
        selected_features (list): List of features to select
        scaler (StandardScaler): Scaler for feature normalization
        
    Returns:
        tuple: (processed_data, original_data)
    """
    try:
        # Validate features
        missing_features = [f for f in selected_features if f not in packet_data]
        if missing_features:
            raise ValueError(f"Missing required features in packet data: {missing_features}")
        
        # Convert to DataFrame with a single row
        df = pd.DataFrame([packet_data])
        
        # Ensure proper order of features
        X = df[selected_features]
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        logger.info("Single packet data processed successfully")
        return X_scaled, df
    except Exception as e:
        logger.error(f"Error processing packet data: {str(e)}")
        raise

def generate_sample_data(selected_features, num_samples=1):
    """
    Generate sample network packet data for testing or demonstration.
    
    Args:
        selected_features (list): List of features to generate
        num_samples (int): Number of samples to generate
        
    Returns:
        pandas.DataFrame: Generated sample data
    """
    try:
        sample_data = {}
        
        for feature in selected_features:
            # Generate appropriate random values based on feature name
            if 'duration' in feature:
                # Duration in microseconds (0 to 2s)
                sample_data[feature] = np.random.randint(0, 2000000, num_samples)
            elif 'packet_length' in feature:
                # Packet length in bytes (20 to 1500)
                sample_data[feature] = np.random.randint(20, 1500, num_samples)
            elif 'port' in feature:
                # Port number (1 to 65535)
                sample_data[feature] = np.random.randint(1, 65536, num_samples)
            elif 'flag' in feature:
                # Flag count (0 to 5)
                sample_data[feature] = np.random.randint(0, 6, num_samples)
            elif 'packets/s' in feature:
                # Packets per second (1 to 1000)
                sample_data[feature] = np.random.randint(1, 1000, num_samples)
            elif 'iat' in feature:
                # Inter-arrival time in microseconds (0 to 1s)
                sample_data[feature] = np.random.randint(0, 1000000, num_samples)
            elif 'ratio' in feature:
                # Ratio (0 to 10)
                sample_data[feature] = np.random.uniform(0, 10, num_samples)
            elif 'win' in feature:
                # Window size (0 to 65535)
                sample_data[feature] = np.random.randint(0, 65536, num_samples)
            else:
                # Default random value (0 to 1000)
                sample_data[feature] = np.random.randint(0, 1000, num_samples)
        
        df = pd.DataFrame(sample_data)
        logger.info(f"Generated {num_samples} sample data rows successfully")
        return df
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        raise

def validate_csv_headers(file_path, required_features):
    """
    Validate that a CSV file contains all required headers.
    
    Args:
        file_path (str): Path to the CSV file
        required_features (list): List of required features
        
    Returns:
        tuple: (is_valid, missing_features)
    """
    try:
        # Read just the header row
        df = pd.read_csv(file_path, nrows=0)
        
        # Check for missing features
        missing_features = [f for f in required_features if f not in df.columns]
        
        is_valid = len(missing_features) == 0
        return is_valid, missing_features
    except Exception as e:
        logger.error(f"Error validating CSV headers: {str(e)}")
        return False, ["Error reading file"]