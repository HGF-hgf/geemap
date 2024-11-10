from airtable import Airtable

# Thay 'base_id' và 'api_key' bằng thông tin của bạn
base_id = 'appfp2UxnBrJ07HB6'
table_name = 'customer'
api_key = 'patRUhLatYudRAVNz.935f51e1657c0dba3bf0a6cc8395456f8525c05a2d6e6927961722da24e7db56'

# Kết nối với Airtable
airtable = Airtable(base_id, table_name, api_key)

# Thêm một bản ghi vào Airtable
def add_record(data):
    airtable.insert(data)
    print("Record added successfully!")

# Truy xuất dữ liệu từ Airtable
def get_records():
    records = airtable.get_all()
    for record in records:
        print(record['fields'])

# Xóa một bản ghi theo ID
def delete_record(record_id):
    airtable.delete(record_id)
    print("Record deleted successfully!")

# Ví dụ sử dụng
data = {"Name": "John Doe", "Phone Number": "(123) 456-456", "Address": "New York"}
add_record(data)
get_records()
