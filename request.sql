1. Viết 1 API method GET /api/count input từ ngày đến ngày, có yêu cầu token tạm thời hardcode. Validate token ( REPLACE các mess mặc định thành " Token không đúng. Vui lòng kiểm tra lại"
2. App chỉ quét các hóa đơn đang gửi được kí trong 6h tính đến thời điểm job start và 1 tiếng chạy lần ( chỉ quét db 6h gần nhất ) ( xử lý bằng SQL ) 
3. Thêm 1 file check_point lưu thời điểm app kết thúc scan lần cuối ( file chỉ chứa 1 dòng ) 
4. Trường hợp app off  ko chạy đúng chu kì 1 tiếng 1 lần ( 2h sau thời điểm check_point app chưa chạy đc coi là app off ) thì khi app chạy lại thì phải quét từ check_point đến thời điểm app chạy. sau đó quay về logic ở yêu cầu 2
5. Xóa app_log 3 ngày 1 lần
6. Cho phép cấu hình các connectstring cần quét tại file cấu hình. nếu file có dữ liệu thì chỉ quét các connectstring đc cấu hình, nếu file trống quét như logic ở yêu cầu 2.
7. Gửi telegram khi sinh ra file trong error_invoice.