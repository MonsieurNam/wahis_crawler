import serverless_wsgi
# Import đối tượng 'app' từ tệp app.py gốc của bạn
from app import app

def handler(event, context):
  """
  Đây là hàm xử lý chính mà Netlify sẽ gọi.
  serverless_wsgi sẽ lo việc chuyển đổi yêu cầu từ Netlify
  thành một định dạng mà Flask có thể hiểu được.
  """
  return serverless_wsgi.handle(app, event, context)