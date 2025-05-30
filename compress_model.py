import joblib

# Load the original model
model = joblib.load('models/final_model.joblib')

# Save it again with compression (level 3 is a good balance)
joblib.dump(model, 'models/final_model_compressed.joblib', compress=3)

print('Model compressed and saved as models/final_model_compressed.joblib') 