from flask import Flask, request, jsonify, render_template
from airtable import Airtable

app = Flask(__name__)

# Airtable configuration
base_id = 'appfp2UxnBrJ07HB6'
table_name = 'customer'
api_key = 'patRUhLatYudRAVNz.935f51e1657c0dba3bf0a6cc8395456f8525c05a2d6e6927961722da24e7db56'
airtable = Airtable(base_id, table_name, api_key)

# Add a record to Airtable
def add_record(data):
    airtable.insert(data)
    print("Record added successfully!")

# Retrieve records from Airtable
def get_records():
    records = airtable.get_all()
    for record in records:
        print(record['fields'])

# Delete a record by ID
def delete_record(record_id):
    airtable.delete(record_id)
    print("Record deleted successfully!")

@app.route('/')
def index():
    return render_template('chat.html')

# Chatbot endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    session_id = request.json.get('session_id')

    # Initialize session data if not present
    if session_id not in session_data:
        session_data[session_id] = {}

    # Simulate a simple state machine for the chatbot
    if 'asked_to_be_customer' not in session_data[session_id]:
        session_data[session_id]['asked_to_be_customer'] = True
        return jsonify({'message': 'Bạn có muốn trở thành khách hàng tiềm năng của chúng tôi để sau này chúng tôi sẽ hỗ trợ thông tin cho bạn về việc bảo trì, cải tiến hệ thống hay cần liên lạc hỗ trợ,...? (yes/no)'})
    elif 'is_customer' not in session_data[session_id]:
        if user_input.lower() in ['yes', 'y', 'có', 'đồng ý']:
            session_data[session_id]['is_customer'] = True
            return jsonify({'message': 'Vui lòng cung cấp tên của bạn.'})
        else:
            session_data[session_id]['is_customer'] = False
            return jsonify({'message': 'Cảm ơn bạn đã quan tâm! Nếu bạn cần hỗ trợ thêm, hãy liên hệ với chúng tôi.'})
    elif session_data[session_id]['is_customer']:
        if 'name' not in session_data[session_id]:
            session_data[session_id]['name'] = user_input
            return jsonify({'message': 'Vui lòng cung cấp số điện thoại của bạn.'})
        elif 'phone_number' not in session_data[session_id]:
            session_data[session_id]['phone_number'] = user_input
            return jsonify({'message': 'Vui lòng cung cấp địa chỉ của bạn.'})
        elif 'address' not in session_data[session_id]:
            session_data[session_id]['address'] = user_input
            # Save the data to Airtable
            data = {
                'Name': session_data[session_id]['name'],
                'Phone Number': session_data[session_id]['phone_number'],
                'Address': session_data[session_id]['address']
            }
            add_record(data)
            return jsonify({'message': 'Cảm ơn bạn! Thông tin của bạn đã được lưu.'})

# Session data to keep track of user inputs
session_data = {}

if __name__ == '__main__':
    app.run(debug=True)