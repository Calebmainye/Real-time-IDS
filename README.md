# Real-time Intrusion Detection System

A machine learning-based Intrusion Detection System (IDS) that effectively identifies, classifies, and reports unauthorized access in network traffic while minimizing false positives.

## 🚀 Features

- Real-time network traffic monitoring and analysis
- Machine learning-based intrusion detection
- Reduced false positive alerts
- Web-based dashboard for monitoring and alerts
- Multiple input methods (file upload, manual input, real-time capture)
- User authentication and secure access
- Detailed alert system with confidence scores
- Performance metrics and visualization

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/real-time-ids.git
cd real-time-ids
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## 🏗️ Project Structure

```
real-time-ids/
├── app.py                 # Main Flask application
├── models/               # Trained models and related files
│   ├── final_model.joblib
│   ├── scaler.pkl
│   └── selected_features.csv
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS, images)
├── utils/               # Utility functions
├── test/                # Test cases
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## 🚀 Usage

1. Start the application:
```bash
python app.py
```

2. Access the web interface:
```
http://localhost:5000
```

3. Login with default credentials:
- Email: admin@example.com
- Password: admin123

## 🔧 Configuration

The system can be configured through the following files:

- `config.py`: Main configuration file
- `models/optimal_threshold.txt`: Detection threshold settings
- `models/selected_features.csv`: Feature selection configuration

## 📊 Model Performance

-Evaluation Results for Random Forest:
-Accuracy: 0.9977
-Precision: 0.9968
-Recall: 0.9978
-F1 Score: 0.9973
-False Positive Rate: 0.0024
-False Negative Rate: 0.0022
-Specificity: 0.9976
-AUC: 0.9999
-Execution Time: 11.06 seconds

## 📝 API Documentation

### Endpoints

- `GET /`: Home page
- `POST /predict-file`: File upload for analysis
- `POST /predict-manual`: Manual input for analysis
- `GET /api/alerts`: Get current alerts
- `GET /monitor`: Real-time monitoring dashboard

## 🔒 Security Features

- User authentication
- Session management
- Secure data handling
- Role-based access control
- Audit logging

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Cale Mainye 

## 🙏 Acknowledgments

- CICIDS2017 dataset
- Scikit-learn
- Flask
- All other open-source libraries used in this project

## 📞 Contact

Your Name - [@gmail](mainyecaleb02@gmail.com)

## 🔄 Future Improvements

- Deep learning integration
- Automated response system
- Advanced feature engineering
- Cloud deployment
- Mobile application
