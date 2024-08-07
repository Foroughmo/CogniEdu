import os
from flask import Flask, request
from initial_import import perform_initial_import
from continuous_sync import perform_continuous_sync
from db_operations import get_db_connection, close_db_connection
from utils import error_handler, setup_logger

app = Flask(__name__)
logger = setup_logger(__name__)

@app.route('/trigger-sync', methods=['POST'])
@error_handler
def trigger_sync():
    # Your existing trigger_sync code here
    return 'Sync process completed', 200

@app.route('/health', methods=['GET'])
def health_check():
    return 'Healthy', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)