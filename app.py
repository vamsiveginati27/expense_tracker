from app import create_app
from datetime import timedelta

app = create_app()

# Configure JWT expiration
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
