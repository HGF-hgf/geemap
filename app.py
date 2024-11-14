from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import requests
from airtable import Airtable
import google.generativeai as genai
import uvicorn

app = FastAPI()
GEMINI_KEY = 'AIzaSyBVT_FFh6FL7yR5YBBm0TVRmHQzQkqoLFo'
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Airtable configuration
base_id = 'appfp2UxnBrJ07HB6'
table_name = 'customer'
api_key = 'patRUhLatYudRAVNz.935f51e1657c0dba3bf0a6cc8395456f8525c05a2d6e6927961722da24e7db56'
airtable = Airtable(base_id, table_name, api_key)

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

session_data = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/chat.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/chatbot")
async def chatbot(request: ChatRequest):
    user_input = request.message
    session_id = request.session_id

    # Initialize session data if not present
    if session_id not in session_data:
        session_data[session_id] = {}

    # Simulate a simple state machine for the chatbot
    if 'asked_to_be_customer' not in session_data[session_id]:
        session_data[session_id]['asked_to_be_customer'] = True
        return JSONResponse(content={'message': model.generate_content('Generate a question to ask if the user wants to be a potential customer, follow this format Bạn có muốn trở thành khách hàng tiềm năng của chúng tôi để sau này chúng tôi sẽ hỗ trợ thông tin cho bạn về việc bảo trì, cải tiến hệ thống hay cần liên lạc hỗ trợ,...? (yes/no)').text})
    elif 'is_customer' not in session_data[session_id]:
        if user_input.lower() in ['yes', 'y', 'có', 'đồng ý']:
            session_data[session_id]['is_customer'] = True
            return JSONResponse(content={'message': model.generate_content('Generate a question to ask for name').text})
        else:
            session_data[session_id]['is_customer'] = False
            return JSONResponse(content={'message': 'Cảm ơn bạn đã quan tâm! Nếu bạn cần hỗ trợ thêm, hãy liên hệ với chúng tôi.'})
    elif session_data[session_id]['is_customer']:
        if 'name' not in session_data[session_id]:
            session_data[session_id]['name'] = user_input
            return JSONResponse(content={'message': model.generate_content('Generate a question to ask for phone number').text})
        elif 'phone_number' not in session_data[session_id]:
            session_data[session_id]['phone_number'] = user_input
            return JSONResponse(content={'message': model.generate_content('Generate a question to ask for address').text})
        elif 'address' not in session_data[session_id]:
            session_data[session_id]['address'] = user_input
            # Save the data to Airtable
            data = {
                'Name': session_data[session_id]['name'],
                'Phone Number': session_data[session_id]['phone_number'],
                'Address': session_data[session_id]['address']
            }
            add_record(data)
            return JSONResponse(content={'message': 'Cảm ơn bạn! Thông tin của bạn đã được lưu.'})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)