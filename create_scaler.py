import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle

# Load the selected features
model_dir = os.path.join(os.path.dirname(__file__), 'models')
selected_features = pd.read_csv(os.path.join(model_dir, 'selected_features.csv'), header=None)[0].tolist()

# Creating a sample dataset with reasonable ranges for network traffic features
# These ranges are based on typical network traffic characteristics
sample_data = {
    'destination_port': np.random.uniform(1, 65535, 1000),  # Destination port number
    'flow_duration': np.random.uniform(0, 1000, 1000),  # Flow duration in seconds
    'fwd_packet_length_max': np.random.uniform(0, 1500, 1000),  # Maximum forward packet length
    'fwd_packet_length_min': np.random.uniform(0, 1500, 1000),  # Minimum forward packet length
    'fwd_packet_length_mean': np.random.uniform(0, 1500, 1000),  # Mean forward packet length
    'bwd_packet_length_max': np.random.uniform(0, 1500, 1000),  # Maximum backward packet length
    'bwd_packet_length_min': np.random.uniform(0, 1500, 1000),  # Minimum backward packet length
    'flow_packets/s': np.random.uniform(0, 1000, 1000),  # Flow packets per second
    'flow_iat_mean': np.random.uniform(0, 1000, 1000),  # Mean flow inter-arrival time
    'flow_iat_std': np.random.uniform(0, 1000, 1000),  # Standard deviation of flow inter-arrival time
    'flow_iat_max': np.random.uniform(0, 1000, 1000),  # Maximum flow inter-arrival time
    'fwd_iat_mean': np.random.uniform(0, 1000, 1000),  # Mean forward inter-arrival time
    'fwd_iat_std': np.random.uniform(0, 1000, 1000),  # Standard deviation of forward inter-arrival time
    'fwd_iat_min': np.random.uniform(0, 1000, 1000),  # Minimum forward inter-arrival time
    'bwd_iat_std': np.random.uniform(0, 1000, 1000),  # Standard deviation of backward inter-arrival time
    'bwd_iat_max': np.random.uniform(0, 1000, 1000),  # Maximum backward inter-arrival time
    'bwd_iat_min': np.random.uniform(0, 1000, 1000),  # Minimum backward inter-arrival time
    'fwd_psh_flags': np.random.uniform(0, 1, 1000),  # Forward PSH flags
    'bwd_packets/s': np.random.uniform(0, 1000, 1000),  # Backward packets per second
    'min_packet_length': np.random.uniform(0, 1500, 1000),  # Minimum packet length
    'max_packet_length': np.random.uniform(0, 1500, 1000),  # Maximum packet length
    'packet_length_mean': np.random.uniform(0, 1500, 1000),  # Mean packet length
    'packet_length_variance': np.random.uniform(0, 1000, 1000),  # Packet length variance
    'fin_flag_count': np.random.uniform(0, 1, 1000),  # FIN flag count
    'psh_flag_count': np.random.uniform(0, 1, 1000),  # PSH flag count
    'ack_flag_count': np.random.uniform(0, 1, 1000),  # ACK flag count
    'urg_flag_count': np.random.uniform(0, 1, 1000),  # URG flag count
    'down/up_ratio': np.random.uniform(0, 1, 1000),  # Download/upload ratio
    'init_win_bytes_backward': np.random.uniform(0, 65535, 1000),  # Initial window bytes backward
    'idle_std': np.random.uniform(0, 1000, 1000)  # Standard deviation of idle time
}

# Convert to DataFrame
df = pd.DataFrame(sample_data)

# Create and fit the scaler
scaler = StandardScaler()
scaler.fit(df[selected_features])

# Save the scaler
scaler_path = os.path.join(model_dir, 'scaler.pkl')
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)

print(f"New scaler created and saved to {scaler_path}") 