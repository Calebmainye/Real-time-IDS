"""
Prediction logic for the intrusion detection system.
This module handles loading the model and making predictions
on network traffic data.
"""

import joblib
import numpy as np
import pandas as pd
import os
import logging
import pickle
from datetime import datetime
import uuid
from sklearn.ensemble import RandomForestClassifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntrusionDetector:
    """
    Class for loading and using the intrusion detection model.
    """
    
    def __init__(self, model_dir):
        """
        Initialize the intrusion detector.
        
        Args:
            model_dir (str): Directory containing the model files
        """
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.threshold = 0.5
        self.selected_features = []
        
        self.load_model()
        
    def load_model(self):
        """
        Load the model and related files from disk.
        """
        try:
            # Load model
            model_path = os.path.join(self.model_dir, 'final_model.joblib')
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
            
            # Load scaler
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"Scaler loaded successfully from {scaler_path}")
            
            # Load threshold
            threshold_path = os.path.join(self.model_dir, 'optimal_threshold.txt')
            with open(threshold_path, 'r') as f:
                self.threshold = float(f.read().strip())
            logger.info(f"Threshold loaded successfully: {self.threshold}")
            
            # Load selected features
            features_path = os.path.join(self.model_dir, 'selected_features.csv')
            self.selected_features = pd.read_csv(features_path, header=None)[0].tolist()
            logger.info(f"Selected features loaded successfully: {len(self.selected_features)} features")
            
            # Get model info
            info_path = os.path.join(self.model_dir, 'model_info.txt')
            with open(info_path, 'r') as f:
                self.model_info = f.read()
            logger.info(f"Model info loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, X_scaled):
        """
        Make predictions on scaled data.
        
        Args:
            X_scaled (numpy.ndarray): Scaled feature data
            
        Returns:
            tuple: (predictions, confidence_scores)
        """
        try:
            # Get confidence scores
            confidence_scores = self.model.predict_proba(X_scaled)[:, 1]
            
            # Apply threshold to get binary predictions
            predictions = (confidence_scores >= self.threshold).astype(int)
            
            logger.info(f"Predictions made successfully: {X_scaled.shape[0]} samples")
            return predictions, confidence_scores
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def predict_file(self, file_path):
        """
        Predict intrusions in a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            dict: Results dictionary
        """
        from .data_processor import process_csv_file
        
        try:
            # Process the file
            X_scaled, original_data = process_csv_file(file_path, self.selected_features, self.scaler)
            
            # Make predictions
            predictions, confidence_scores = self.predict(X_scaled)
            
            # Create results
            results = []
            for i, (pred, conf) in enumerate(zip(predictions, confidence_scores)):
                results.append({
                    'index': i,
                    'is_intrusion': bool(pred),
                    'confidence': float(conf)
                })
            
            # Summary statistics
            total = len(predictions)
            intrusions = int(np.sum(predictions))
            safe = total - intrusions
            
            return {
                'total': total,
                'intrusions': intrusions,
                'safe': safe,
                'results': results
            }
        except Exception as e:
            logger.error(f"Error predicting file: {str(e)}")
            raise
    
    def predict_data(self, data_dict):
        """
        Predict intrusion for a single packet's data.
        
        Args:
            data_dict (dict): Dictionary with feature values
            
        Returns:
            dict: Results dictionary
        """
        from .data_processor import process_packet_data
        
        try:
            # Process the packet data
            X_scaled, _ = process_packet_data(data_dict, self.selected_features, self.scaler)
            
            # Make predictions
            _, confidence = self.predict(X_scaled)
            confidence = float(confidence[0])
            
            # Apply threshold
            is_intrusion = confidence >= self.threshold
            
            # Create alert if intrusion
            alert = None
            if is_intrusion:
                alert = {
                    'id': str(uuid.uuid4()),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'Manual Input',
                    'confidence': confidence,
                    'details': data_dict
                }
            
            return {
                'is_intrusion': bool(is_intrusion),
                'confidence': confidence,
                'threshold': self.threshold,
                'alert': alert
            }
        except Exception as e:
            logger.error(f"Error predicting data: {str(e)}")
            raise
    
    def get_feature_importances(self):
        """
        Get feature importances from the model.
        
        Returns:
            dict: Dictionary mapping feature names to importance values
        """
        try:
            importances = self.model.feature_importances_
            feature_importances = dict(zip(self.selected_features, importances))
            
            # Sort by importance (descending)
            sorted_importances = {
                k: v for k, v in sorted(
                    feature_importances.items(), 
                    key=lambda item: item[1], 
                    reverse=True
                )
            }
            
            return sorted_importances
        except Exception as e:
            logger.error(f"Error getting feature importances: {str(e)}")
            raise
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the model performance on test data.
        
        Args:
            X_test (numpy.ndarray): Test feature data
            y_test (numpy.ndarray): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        try:
            # Scale the test data
            X_test_scaled = self.scaler.transform(X_test)
            
            # Make predictions
            y_pred, y_scores = self.predict(X_test_scaled)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1_score': f1_score(y_test, y_pred),
                'auc_roc': roc_auc_score(y_test, y_scores)
            }
            
            logger.info(f"Model evaluation completed: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def get_model_info(self):
        """
        Get information about the model.
        
        Returns:
            dict: Model information
        """
        try:
            # Parse model info
            info_lines = self.model_info.strip().split('\n')
            info_dict = {}
            
            for line in info_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info_dict[key.strip()] = value.strip()
            
            # Add additional info
            info_dict['threshold'] = self.threshold
            info_dict['num_features'] = len(self.selected_features)
            info_dict['features'] = self.selected_features
            
            if hasattr(self.model, 'n_estimators'):
                info_dict['n_estimators'] = self.model.n_estimators
            
            logger.info(f"Model info retrieved successfully")
            return info_dict
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            raise